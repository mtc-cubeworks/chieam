"""
Metadata Infrastructure Adapters
=================================
Concrete implementations of domain protocols.
Each adapter wraps an existing service to satisfy a protocol contract.
"""
import json
from pathlib import Path
from typing import Any, Optional

from app.domain.protocols.metadata_sync import (
    MetadataReaderProtocol,
    MetadataWriterProtocol,
    MetadataValidatorProtocol,
    ChangeAnalyzerProtocol,
    ModelGeneratorProtocol,
    MigrationManagerProtocol,
    RegistryManagerProtocol,
    ChangeAnalysis,
    FieldChange,
    ChangeType,
)


class JsonMetadataReader:
    """Reads entity metadata from JSON files on disk."""

    def __init__(self):
        self._app_dir = Path(__file__).parent.parent.parent
        self._modules_dir = self._app_dir / "modules"

    def list_all_entities(self) -> list[dict]:
        entities = []
        for module_dir in self._modules_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue
            entities_dir = module_dir / "entities"
            if not entities_dir.exists():
                continue
            for item in entities_dir.iterdir():
                if item.name.startswith("_"):
                    continue
                json_file = None
                if item.is_file() and item.suffix == ".json":
                    json_file = item
                elif item.is_dir():
                    nested_json = item / f"{item.name}.json"
                    if nested_json.exists():
                        json_file = nested_json
                if json_file:
                    try:
                        with open(json_file, "r") as f:
                            data = json.load(f)
                        entities.append({
                            "name": data.get("name", json_file.stem),
                            "label": data.get("label", json_file.stem),
                            "module": data.get("module", module_dir.name),
                            "field_count": len(data.get("fields", [])),
                            "json_path": str(json_file),
                        })
                    except Exception as e:
                        print(f"Error reading {json_file}: {e}")
        return sorted(entities, key=lambda x: (x["module"], x["name"]))

    def get_entity_metadata(self, entity_name: str) -> Optional[dict]:
        json_path = self.get_entity_json_path(entity_name)
        if not json_path:
            return None
        with open(json_path, "r") as f:
            return json.load(f)

    def get_entity_json_path(self, entity_name: str) -> Optional[Path]:
        for module_dir in self._modules_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue
            entities_dir = module_dir / "entities"
            if not entities_dir.exists():
                continue
            flat_path = entities_dir / f"{entity_name}.json"
            if flat_path.exists():
                return flat_path
            nested_path = entities_dir / entity_name / f"{entity_name}.json"
            if nested_path.exists():
                return nested_path
        return None


class JsonMetadataWriter:
    """Writes entity metadata to JSON files and manages backups."""

    def __init__(self, reader: JsonMetadataReader):
        self._reader = reader
        self._app_dir = Path(__file__).parent.parent.parent
        self._backup_dir = self._app_dir.parent / "backups" / "metadata"

    def save_metadata(self, entity_name: str, metadata: dict) -> str:
        json_path = self._reader.get_entity_json_path(entity_name)
        if not json_path:
            raise FileNotFoundError(f"Entity '{entity_name}' JSON not found")
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)
        return str(json_path)

    def create_backup(self, entity_name: str) -> Optional[str]:
        json_path = self._reader.get_entity_json_path(entity_name)
        if not json_path:
            return None
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._backup_dir / f"{entity_name}_{timestamp}.json"
        shutil.copy2(json_path, backup_path)
        return str(backup_path)

    def list_backups(self, entity_name: str) -> list[dict]:
        if not self._backup_dir.exists():
            return []
        from datetime import datetime
        backups = []
        for backup_file in self._backup_dir.glob(f"{entity_name}_*.json"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size,
            })
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def restore_backup(self, entity_name: str, backup_filename: str) -> dict:
        backup_path = self._backup_dir / backup_filename
        if not backup_path.exists():
            return {"success": False, "error": "Backup not found"}
        json_path = self._reader.get_entity_json_path(entity_name)
        if not json_path:
            return {"success": False, "error": f"Entity '{entity_name}' not found"}
        import shutil
        shutil.copy2(backup_path, json_path)
        return {"success": True, "restored_from": str(backup_path)}


# Field types accepted by the system
VALID_FIELD_TYPES = [
    "string", "text", "int", "float", "boolean",
    "date", "datetime", "link", "select", "attach",
    "parent_child_link", "query_link",
    "email", "phone", "currency", "percent", "image", "file",
]


class MetadataValidator:
    """Validates entity metadata structure and values."""

    def validate(self, metadata: dict) -> tuple[bool, list[str]]:
        errors: list[str] = []

        if not metadata.get("name"):
            errors.append("Entity name is required")
        if not metadata.get("module"):
            errors.append("Module is required")
        icon = metadata.get("icon")
        if icon is not None and not isinstance(icon, str):
            errors.append("icon must be a string")

        # search_fields
        search_fields = metadata.get("search_fields")
        if search_fields is not None:
            if not isinstance(search_fields, list):
                errors.append("search_fields must be a list of field names")
            else:
                field_names = {f.get("name") for f in metadata.get("fields", []) if f.get("name")}
                for fn in search_fields:
                    if fn not in field_names:
                        errors.append(f"search_fields contains invalid field: {fn}")

        # fields
        fields = metadata.get("fields", [])
        seen_names: set[str] = set()
        for i, field in enumerate(fields):
            if not field.get("name"):
                errors.append(f"Field {i+1}: name is required")
                continue
            name = field["name"]
            if name in seen_names:
                errors.append(f"Duplicate field name: {name}")
            seen_names.add(name)

            ft = field.get("field_type", "string")
            if ft not in VALID_FIELD_TYPES:
                errors.append(f"Field '{name}': invalid type '{ft}'")
            if ft == "link" and not field.get("link_entity"):
                errors.append(f"Field '{name}': link_entity required for link type")
            if ft == "parent_child_link":
                if not field.get("child_entity"):
                    errors.append(f"Field '{name}': child_entity required for parent_child_link type")
                if not field.get("parent_entity"):
                    errors.append(f"Field '{name}': parent_entity required for parent_child_link type")
                if not field.get("child_parent_fk_field"):
                    errors.append(f"Field '{name}': child_parent_fk_field required for parent_child_link type")
            if ft == "query_link":
                query = field.get("query")
                if not query or not isinstance(query, dict):
                    errors.append(f"Field '{name}': query object required for query_link type")
                elif not query.get("key"):
                    errors.append(f"Field '{name}': query.key required for query_link type")

        # links
        links = metadata.get("links")
        if links is not None:
            if not isinstance(links, list):
                errors.append("links must be a list")
            else:
                for i, link in enumerate(links):
                    if not isinstance(link, dict):
                        errors.append(f"links[{i}] must be an object")
                        continue
                    if not link.get("entity"):
                        errors.append(f"links[{i}].entity is required")
                    if not link.get("fk_field"):
                        errors.append(f"links[{i}].fk_field is required")
                    if not link.get("label"):
                        errors.append(f"links[{i}].label is required")
                    for key in ("show_when", "hide_when"):
                        cond = link.get(key)
                        if cond is None:
                            continue
                        if not isinstance(cond, dict):
                            errors.append(f"links[{i}].{key} must be an object")
                            continue
                        for k, v in cond.items():
                            if not isinstance(v, list):
                                errors.append(f"links[{i}].{key}.{k} must be a list")
                            elif not all(isinstance(x, str) for x in v):
                                errors.append(f"links[{i}].{key}.{k} must be a list of strings")

        # form_state
        form_state = metadata.get("form_state")
        if form_state is not None:
            if not isinstance(form_state, dict):
                errors.append("form_state must be an object")
            else:
                tab_rules = form_state.get("tab_rules")
                if tab_rules is not None:
                    if not isinstance(tab_rules, list):
                        errors.append("form_state.tab_rules must be a list")
                    else:
                        for i, tr in enumerate(tab_rules):
                            if not isinstance(tr, dict):
                                errors.append(f"form_state.tab_rules[{i}] must be an object")
                                continue
                            if not tr.get("entity"):
                                errors.append(f"form_state.tab_rules[{i}].entity is required")

        # attachment_config
        attachment_config = metadata.get("attachment_config")
        if attachment_config is not None:
            if not isinstance(attachment_config, dict):
                errors.append("attachment_config must be an object")
            else:
                max_att = attachment_config.get("max_attachments")
                if max_att is not None and (not isinstance(max_att, int) or max_att < 1):
                    errors.append("attachment_config.max_attachments must be a positive integer")
                max_size = attachment_config.get("max_file_size_mb")
                if max_size is not None and (not isinstance(max_size, (int, float)) or max_size <= 0):
                    errors.append("attachment_config.max_file_size_mb must be a positive number")
                allowed_ext = attachment_config.get("allowed_extensions")
                if allowed_ext is not None:
                    if not isinstance(allowed_ext, list) or not all(isinstance(e, str) for e in allowed_ext):
                        errors.append("attachment_config.allowed_extensions must be a list of strings")

        # field-level depends_on
        for i, field_item in enumerate(metadata.get("fields", [])):
            for dep_key in ("display_depends_on", "mandatory_depends_on"):
                dep_val = field_item.get(dep_key)
                if dep_val is not None and not isinstance(dep_val, str):
                    fname = field_item.get("name", f"field[{i}]")
                    errors.append(f"Field '{fname}': {dep_key} must be a string")

        return len(errors) == 0, errors


class MetadataChangeAnalyzer:
    """Analyzes changes between current and new metadata."""

    def __init__(self, reader: JsonMetadataReader):
        self._reader = reader

    def analyze(self, entity_name: str, new_metadata: dict) -> ChangeAnalysis:
        changes = ChangeAnalysis(entity_name=entity_name)
        current = self._reader.get_entity_metadata(entity_name)
        if not current:
            changes.add_change(FieldChange(
                field_name="*",
                change_type=ChangeType.SAFE,
                description="New entity creation",
            ))
            return changes

        current_fields = {f["name"]: f for f in current.get("fields", [])}
        new_fields = {f["name"]: f for f in new_metadata.get("fields", [])}

        # Removed fields (DANGEROUS)
        for name in current_fields:
            if name not in new_fields:
                changes.add_change(FieldChange(
                    field_name=name,
                    change_type=ChangeType.DANGEROUS,
                    description=f"Field '{name}' will be removed",
                    old_value=current_fields[name],
                    new_value=None,
                ))

        # Added fields (SAFE)
        for name in new_fields:
            if name not in current_fields:
                changes.add_change(FieldChange(
                    field_name=name,
                    change_type=ChangeType.SAFE,
                    description=f"New field '{name}' will be added",
                    old_value=None,
                    new_value=new_fields[name],
                ))

        # Modified fields
        for name in current_fields:
            if name not in new_fields:
                continue
            old_f = current_fields[name]
            new_f = new_fields[name]

            # Type change (DANGEROUS)
            if old_f.get("field_type") != new_f.get("field_type"):
                changes.add_change(FieldChange(
                    field_name=name,
                    change_type=ChangeType.DANGEROUS,
                    description=f"Field '{name}' type changed from '{old_f.get('field_type')}' to '{new_f.get('field_type')}'",
                    old_value=old_f.get("field_type"),
                    new_value=new_f.get("field_type"),
                ))

            # Required change
            old_req = old_f.get("required", False)
            new_req = new_f.get("required", False)
            if old_req != new_req:
                ct = ChangeType.DANGEROUS if new_req else ChangeType.SAFE
                desc = f"Field '{name}' is now {'required' if new_req else 'optional'}"
                changes.add_change(FieldChange(
                    field_name=name,
                    change_type=ct,
                    description=desc,
                    old_value=old_req,
                    new_value=new_req,
                ))

            # Label change (SAFE)
            if old_f.get("label") != new_f.get("label"):
                changes.add_change(FieldChange(
                    field_name=name,
                    change_type=ChangeType.SAFE,
                    description=f"Field '{name}' label changed",
                    old_value=old_f.get("label"),
                    new_value=new_f.get("label"),
                ))

            # Hidden/readonly changes (SAFE - UI only)
            for prop in ("hidden", "readonly"):
                if old_f.get(prop) != new_f.get(prop):
                    changes.add_change(FieldChange(
                        field_name=name,
                        change_type=ChangeType.SAFE,
                        description=f"Field '{name}' {prop} changed",
                        old_value=old_f.get(prop),
                        new_value=new_f.get(prop),
                    ))

        return changes


class ModelGeneratorAdapter:
    """Wraps ModelGeneratorService to satisfy ModelGeneratorProtocol."""

    def __init__(self):
        from app.infrastructure.metadata.model_generator import ModelGeneratorService
        self._service = ModelGeneratorService()

    def generate_model_code(self, metadata: dict) -> str:
        return self._service.generate_model_code(metadata)

    def update_model_file(self, metadata: dict, backup: bool = True, **kwargs) -> dict:
        return self._service.update_model_file(metadata, backup=backup, **kwargs)

    def get_model_diff(self, metadata: dict, **kwargs) -> dict:
        return self._service.get_model_diff(metadata, **kwargs)


class MigrationManagerAdapter:
    """Wraps MigrationService to satisfy MigrationManagerProtocol."""

    def __init__(self):
        from app.infrastructure.metadata.migration_service import MigrationService
        self._service = MigrationService()

    def generate_migration(self, message: str) -> dict:
        return self._service.generate_migration(message)

    def apply_migration(self, revision: str = "head") -> dict:
        return self._service.apply_migration(revision)

    def rollback_migration(self, steps: int = 1) -> dict:
        return self._service.rollback_migration(steps)

    def get_current_revision(self) -> dict:
        return self._service.get_current_revision()

    def get_pending_migrations(self) -> dict:
        return self._service.get_pending_migrations()

    def check_migration_needed(self) -> dict:
        return self._service.check_migration_needed()


class RegistryManagerAdapter:
    """Manages the in-memory MetaRegistry."""

    def reload_entity(self, entity_name: str, json_path: Any) -> bool:
        from app.entities import load_entity_from_json
        from app.meta.registry import MetaRegistry
        try:
            entity_meta = load_entity_from_json(json_path)
            if entity_meta:
                MetaRegistry.register(entity_meta)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to reload entity {entity_name}: {e}")
            return False

    def reload_all(self) -> int:
        from app.entities import load_all_entities
        from app.meta.registry import MetaRegistry
        MetaRegistry._entities.clear()
        load_all_entities()
        return len(MetaRegistry._entities)
