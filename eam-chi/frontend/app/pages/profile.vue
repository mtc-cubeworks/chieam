<script setup lang="ts">
const { apiFetch, baseURL } = useApiFetch();
const toast = useToast();
const router = useRouter();

interface ProfileData {
  id: string;
  username: string;
  email: string;
  full_name: string;
  first_name: string | null;
  last_name: string | null;
  contact_number: string | null;
  department: string | null;
  site: string | null;
  employee_id: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

const profile = ref<ProfileData | null>(null);
const loading = ref(true);
const saving = ref(false);
const isEditMode = ref(false);

const formData = reactive({
  full_name: "",
  first_name: "",
  last_name: "",
  contact_number: "",
  email: "",
});

const fields = [
  { name: "username", label: "Username", readonly: true },
  { name: "employee_id", label: "Employee ID", readonly: true },
  { name: "full_name", label: "Full Name", editable: true },
  { name: "first_name", label: "First Name", editable: true },
  { name: "last_name", label: "Last Name", editable: true },
  { name: "email", label: "Email", editable: true, type: "email" },
  { name: "contact_number", label: "Contact Number", editable: true },
  { name: "department", label: "Department", readonly: true },
  { name: "site", label: "Site", readonly: true },
];

const syncFormFromProfile = () => {
  if (!profile.value) return;
  formData.full_name = profile.value.full_name || "";
  formData.first_name = profile.value.first_name || "";
  formData.last_name = profile.value.last_name || "";
  formData.contact_number = profile.value.contact_number || "";
  formData.email = profile.value.email || "";
};

const loadProfile = async () => {
  loading.value = true;
  try {
    const res = await apiFetch<{ status: string; data: ProfileData }>(
      `${baseURL}/profile`,
    );
    if (res.status === "success") {
      profile.value = res.data;
      syncFormFromProfile();
    }
  } catch (err: any) {
    toast.add({
      title: "Failed to load profile",
      description: err?.message,
      color: "error",
    });
  } finally {
    loading.value = false;
  }
};

const handleSave = async () => {
  saving.value = true;
  try {
    const res = await apiFetch<{ status: string; message: string }>(
      `${baseURL}/profile`,
      { method: "PUT", body: formData },
    );
    if (res.status === "success") {
      toast.add({ title: res.message || "Profile updated", color: "success" });
      isEditMode.value = false;
      await loadProfile();
    } else {
      toast.add({ title: "Update failed", color: "error" });
    }
  } catch (err: any) {
    toast.add({
      title: "Failed to update profile",
      description: err?.message,
      color: "error",
    });
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  syncFormFromProfile();
  isEditMode.value = false;
};

const getFieldValue = (fieldName: string): string => {
  if (!profile.value) return "";
  return (profile.value as any)[fieldName] || "";
};

onMounted(loadProfile);

definePageMeta({ middleware: "auth" as any });
</script>

<template>
  <div class="h-full min-h-0 flex flex-col gap-6 px-3 py-3">
    <!-- Header -->
    <div class="flex items-center gap-2">
      <UButton
        variant="ghost"
        icon="i-lucide-arrow-left"
        @click="router.go(-1)"
      />
      <div class="flex-1 flex items-center gap-2">
        <UAvatar
          v-if="profile"
          size="md"
          :alt="profile.full_name"
          class="mr-1"
        />
        <h1 class="text-2xl font-bold">
          {{ profile?.full_name || "My Profile" }}
        </h1>
        <UBadge
          v-if="profile?.is_superuser"
          variant="subtle"
          color="primary"
          size="sm"
        >
          Superuser
        </UBadge>
      </div>

      <!-- Actions -->
      <div class="flex gap-2">
        <template v-if="isEditMode">
          <UButton :loading="saving" @click="handleSave">Save</UButton>
          <UButton
            variant="outline"
            icon="i-lucide-x"
            :disabled="saving"
            @click="handleCancel"
          />
        </template>
        <template v-else>
          <UButton
            v-if="!loading"
            icon="i-lucide-pencil"
            @click="isEditMode = true"
          >
            Edit
          </UButton>
        </template>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="space-y-6 mt-3">
      <div class="flex gap-4 ml-4 mb-3">
        <USkeleton v-for="i in 2" :key="i" class="h-4 w-24" />
      </div>
      <USeparator />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div v-for="i in 8" :key="i" class="space-y-2">
          <USkeleton class="h-4 w-24" />
          <USkeleton class="h-8 w-full" />
        </div>
      </div>
    </div>

    <!-- Profile Form -->
    <div v-else-if="profile" class="flex-1 min-h-0 overflow-y-auto pb-8">
      <UTabs
        :items="[
          { label: 'Details', value: 'details' },
          { label: 'Account', value: 'account' },
        ]"
        default-value="details"
        variant="link"
        size="md"
        class="w-full"
      >
        <template #content="{ item }">
          <!-- Details Tab -->
          <div v-if="item.value === 'details'" class="space-y-6 mt-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div v-for="field in fields" :key="field.name" class="space-y-2">
                <UFormField :label="field.label">
                  <UInput
                    v-if="field.editable && isEditMode"
                    v-model="(formData as any)[field.name]"
                    :type="field.type || 'text'"
                    :placeholder="field.label"
                    class="w-full"
                  />
                  <UInput
                    v-else
                    :model-value="getFieldValue(field.name)"
                    disabled
                    class="w-full"
                  />
                </UFormField>
              </div>
            </div>
          </div>

          <!-- Account Tab -->
          <div v-else-if="item.value === 'account'" class="space-y-6 mt-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <UFormField label="User ID">
                <UInput :model-value="profile.id" disabled class="w-full" />
              </UFormField>
              <UFormField label="Username">
                <UInput
                  :model-value="profile.username"
                  disabled
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Status">
                <UInput
                  :model-value="profile.is_active ? 'Active' : 'Inactive'"
                  disabled
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Role">
                <UInput
                  :model-value="
                    profile.is_superuser ? 'Superuser' : 'Standard User'
                  "
                  disabled
                  class="w-full"
                />
              </UFormField>
            </div>
          </div>
        </template>
      </UTabs>
    </div>
  </div>
</template>
