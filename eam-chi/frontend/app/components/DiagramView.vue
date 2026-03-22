<script setup lang="ts">
import cytoscape from "cytoscape";
import type { EntityMeta } from "~/composables/useApiTypes";
import { usePositionDiagram } from "~/composables/usePositionDiagram";

type FilterOption = { label: string; value: string };

const props = defineProps<{
  entityName: string;
  entityMeta: EntityMeta | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  view: [row: any];
}>();

const { loadDiagramData: fetchDiagramData } = usePositionDiagram();
const toast = useToast();
const cyContainer = ref<HTMLElement | null>(null);
const cy = ref<cytoscape.Core | null>(null);
const diagramLoading = ref(true);
const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);
const locationOptions = ref<FilterOption[]>([]);
const systemOptions = ref<FilterOption[]>([]);
const selectedLocation = ref<string | undefined>(undefined);
const selectedSystem = ref<string | undefined>(undefined);
let renderScheduled = false;

const scheduleRender = () => {
  if (renderScheduled) return;
  renderScheduled = true;
  nextTick(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        renderScheduled = false;
        renderDiagram();
      });
    });
  });
};

const loadDiagramData = async () => {
  diagramLoading.value = true;
  try {
    const response = await fetchDiagramData({
      location: selectedLocation.value,
      system: selectedSystem.value,
    });

    nodes.value = response.nodes;
    edges.value = response.edges;
    locationOptions.value = response.locationOptions;
    systemOptions.value = response.systemOptions;
    selectedLocation.value = response.selectedLocation;
    selectedSystem.value = response.selectedSystem;

    if (nodes.value.length === 0) {
      console.warn("No nodes found - entity may not exist or no permissions");
    }
  } catch (err) {
    console.error("Failed to load diagram data:", err);
    // Show error message to user
    toast.add({
      title: "Error",
      description: "Failed to load diagram data. Check console for details.",
      color: "error",
    });
  } finally {
    diagramLoading.value = false;
  }
};

const renderDiagram = () => {
  if (!cyContainer.value) {
    console.warn("cyContainer ref is null - cannot render diagram");
    return;
  }

  // Cytoscape can crash if initialized while the container has zero size
  // (e.g. during view transitions / v-if swaps).
  const rect = cyContainer.value.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) {
    console.warn("cyContainer has zero size - delaying diagram render");
    scheduleRender();
    return;
  }

  if (!nodes.value.length) {
    console.warn("No nodes data - cannot render diagram");
    return;
  }

  if (cy.value) {
    cy.value.destroy();
    cy.value = null;
  }

  try {
    cy.value = cytoscape({
      container: cyContainer.value,
      elements: { nodes: nodes.value, edges: edges.value },
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "text-valign": "bottom",
            "text-halign": "center",
            "font-size": "11px",
            "text-margin-y": 8,
            "background-color": "#6366f1",
            width: 36,
            height: 36,
            "border-width": 2,
            "border-color": "#4f46e5",
            color: "#374151",
          },
        },
        {
          selector: "node[?asset]",
          style: {
            "background-color": "#10b981",
            "border-color": "#059669",
          },
        },
        {
          selector: "node[image]",
          style: {
            "background-color": "#ffffff",
            "border-color": "#94a3b8",
            "background-image": (ele: any) => ele.data("image") || "none",
            "background-fit": "none",
            "background-clip": "none",
            "background-width": "70%",
            "background-height": "70%",
            "background-position-x": "50%",
            "background-position-y": "50%",
            "background-image-containment": "over",
            "background-opacity": 1,
          },
        },
        {
          selector: "node:selected",
          style: {
            "background-color": "#f59e0b",
            "border-color": "#d97706",
            "border-width": 3,
          },
        },
        {
          selector: "edge",
          style: {
            label: "data(label)",
            "font-size": "9px",
            "text-rotation": "autorotate",
            "text-margin-y": -10,
            color: "#6b7280",
            width: 2,
            "line-color": "#d1d5db",
            "target-arrow-color": "#9ca3af",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
      ],
      layout: {
        name: "cose",
        animate: true,
        animationDuration: 500,
        nodeRepulsion: () => 8000,
        idealEdgeLength: () => 120,
        gravity: 0.25,
        padding: 40,
      },
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.3,
    });

    cy.value.on("tap", "node", (evt) => {
      const nodeId = evt.target.id();
      const node = nodes.value.find((n: any) => n.data.id === nodeId);
      if (node) {
        emit("view", node);
      }
    });
  } catch (error) {
    console.error("Failed to render cytoscape diagram:", error);
    toast.add({
      title: "Error",
      description: "Failed to render diagram. Check console for details.",
      color: "error",
    });
  }
};

const fitDiagram = () => {
  cy.value?.fit(undefined, 40);
};

const relayoutDiagram = () => {
  if (!cy.value) return;
  cy.value
    .layout({
      name: "cose",
      animate: true,
      animationDuration: 500,
      nodeRepulsion: () => 8000,
      idealEdgeLength: () => 120,
      gravity: 0.25,
      padding: 40,
    } as any)
    .run();
};

watch(
  () => [nodes.value, edges.value],
  () => {
    if (!diagramLoading.value) {
      scheduleRender();
    }
  },
  { deep: true },
);

watch([selectedLocation, selectedSystem], async () => {
  if (diagramLoading.value) return;
  await loadDiagramData();
});

onMounted(async () => {
  await loadDiagramData();
  scheduleRender();
});

onBeforeUnmount(() => {
  if (cy.value) {
    cy.value.destroy();
    cy.value = null;
  }
});
</script>

<template>
  <div class="h-full min-h-0 flex flex-col gap-3">
    <!-- Toolbar -->
    <div
      class="shrink-0 flex items-center justify-between px-4 py-2 border border-muted rounded-lg"
    >
      <div
        class="flex flex-wrap items-center gap-2 text-sm text-muted-foreground"
      >
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-indigo-500 inline-block" />
          Empty Position
        </span>
        <span class="flex items-center gap-1 ml-3">
          <span class="w-3 h-3 rounded-full bg-emerald-500 inline-block" />
          Has Asset
        </span>
        <span class="flex items-center gap-1 ml-3">
          <span
            class="w-3 h-3 rounded-full border border-slate-400 bg-white inline-block"
          />
          Asset Class Icon
        </span>
        <span class="ml-3">
          {{ nodes.length }} nodes · {{ edges.length }} edges
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-2 justify-end">
        <USelectMenu
          v-model="selectedLocation"
          :items="locationOptions"
          value-key="value"
          label-key="label"
          placeholder="All locations"
          clear
          searchable
          class="w-48"
        />
        <USelectMenu
          v-model="selectedSystem"
          :items="systemOptions"
          value-key="value"
          label-key="label"
          placeholder="All systems"
          clear
          searchable
          class="w-48"
        />
        <UButton
          icon="i-lucide-maximize"
          variant="ghost"
          size="xs"
          @click="fitDiagram"
        >
          Fit
        </UButton>
        <UButton
          icon="i-lucide-refresh-cw"
          variant="ghost"
          size="xs"
          :loading="diagramLoading"
          @click="relayoutDiagram"
        >
          Re-layout
        </UButton>
        <UButton
          icon="i-lucide-refresh-cw"
          variant="ghost"
          size="xs"
          :loading="diagramLoading"
          @click="loadDiagramData"
        >
          Reload
        </UButton>
      </div>
    </div>

    <!-- Diagram Container -->
    <div
      v-if="diagramLoading"
      class="flex-1 min-h-0 flex items-center justify-center border border-muted rounded-lg"
    >
      <UIcon
        name="i-lucide-loader-2"
        class="animate-spin h-8 w-8 text-primary"
      />
    </div>

    <div
      v-else-if="nodes.length === 0"
      class="flex-1 min-h-0 flex items-center justify-center text-center border border-muted rounded-lg"
    >
      <div>
        <UIcon
          name="i-lucide-git-branch"
          class="h-12 w-12 mx-auto text-muted-foreground mb-4"
        />
        <h3 class="text-lg font-medium mb-2">No positions found</h3>
        <p class="text-muted-foreground">
          Create positions and relations to see the diagram.
        </p>
      </div>
    </div>

    <div
      v-else
      ref="cyContainer"
      class="flex-1 min-h-0 w-full border border-muted rounded-lg bg-white dark:bg-gray-950 overflow-hidden"
    />
  </div>
</template>
