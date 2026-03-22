/**
 * PM Calendar API Composable
 * ===========================
 * All API calls for the Preventive Maintenance Calendar feature.
 */

export interface PmTask {
  id: string
  activity_name: string
  workflow_state: string
  due_date: string
  start_time: string
  laborer: string
  assigned_to: string | null
  work_order_activity_id: string | null
  planned_maintenance_activity: string | null
  site: string | null
  department: string | null
  notes: string | null
  color: string
}

export interface ActivityOption {
  id: string
  activity_name: string
}

export interface LaborOption {
  id: string
  laborer: string
  labor_type: string
}

export interface TimeSlot {
  value: string
  label: string
}

export interface HolidayItem {
  id: string
  holiday_name: string
  holiday_date: string
}

export interface SiteOption {
  id: string
  site_name: string
}

export interface DepartmentOption {
  id: string
  department_name: string
}

export interface TaskCreatePayload {
  activity_name: string
  due_date: string
  start_time: string
  assigned_to?: string | null
  workflow_state?: string
  site?: string | null
  department?: string | null
  notes?: string | null
}

export interface TaskUpdatePayload {
  activity_name?: string | null
  due_date?: string | null
  start_time?: string | null
  assigned_to?: string | null
  workflow_state?: string | null
  site?: string | null
  department?: string | null
  notes?: string | null
}

export const usePmCalendar = () => {
  const { apiFetch, baseURL } = useApiFetch()

  const fetchTasks = async (year: number, month: number, site?: string, department?: string): Promise<PmTask[]> => {
    const params = new URLSearchParams({ year: String(year), month: String(month) })
    if (site) params.set('site', site)
    if (department) params.set('department', department)

    const response = await apiFetch<{ status: string; data: PmTask[] }>(`${baseURL}/features/pm-calendar/tasks?${params}`)
    return response?.data ?? []
  }

  const fetchWorkOrderActivities = async (year: number, month: number): Promise<PmTask[]> => {
    const params = new URLSearchParams({ year: String(year), month: String(month) })

    const response = await apiFetch<{ status: string; data: PmTask[] }>(`${baseURL}/features/pm-calendar/work-order-activities?${params}`)
    return response?.data ?? []
  }

  const fetchTask = async (taskId: string): Promise<PmTask> => {
    const res = await apiFetch<{ status: string; data: PmTask }>(
      `${baseURL}/features/pm-calendar/tasks/${taskId}`
    )
    return res.data
  }

  const fetchWorkOrderActivity = async (activityId: string): Promise<PmTask> => {
    const res = await apiFetch<{ status: string; data: PmTask }>(
      `${baseURL}/features/pm-calendar/work-order-activities/${activityId}`
    )
    return res.data
  }

  const createTask = async (payload: TaskCreatePayload): Promise<PmTask> => {
    const res = await apiFetch<{ status: string; data: PmTask }>(
      `${baseURL}/features/pm-calendar/tasks`,
      { method: 'POST', body: payload }
    )
    return res.data
  }

  const updateTask = async (taskId: string, payload: TaskUpdatePayload): Promise<PmTask> => {
    const res = await apiFetch<{ status: string; data: PmTask }>(
      `${baseURL}/features/pm-calendar/tasks/${taskId}`,
      { method: 'PUT', body: payload }
    )
    return res.data
  }

  const rescheduleTask = async (taskId: string, dueDate: string): Promise<void> => {
    await apiFetch(
      `${baseURL}/features/pm-calendar/tasks/${taskId}/reschedule`,
      { method: 'PATCH', body: { due_date: dueDate } }
    )
  }

  const updateTaskStatus = async (taskId: string, workflowState: string): Promise<{ id: string; workflow_state: string; color: string }> => {
    const res = await apiFetch<{ status: string; data: { id: string; workflow_state: string; color: string } }>(
      `${baseURL}/features/pm-calendar/tasks/${taskId}/status`,
      { method: 'PATCH', body: { workflow_state: workflowState } }
    )
    return res.data
  }

  const deleteTask = async (taskId: string): Promise<void> => {
    await apiFetch(
      `${baseURL}/features/pm-calendar/tasks/${taskId}`,
      { method: 'DELETE' }
    )
  }

  const fetchActivities = async (): Promise<ActivityOption[]> => {
    const res = await apiFetch<{ status: string; data: ActivityOption[] }>(
      `${baseURL}/features/pm-calendar/activities`
    )
    return res.data || []
  }

  const fetchLabor = async (): Promise<LaborOption[]> => {
    const res = await apiFetch<{ status: string; data: LaborOption[] }>(
      `${baseURL}/features/pm-calendar/labor`
    )
    return res.data || []
  }

  const fetchTimeSlots = async (): Promise<TimeSlot[]> => {
    const res = await apiFetch<{ status: string; data: TimeSlot[] }>(
      `${baseURL}/features/pm-calendar/time-slots`
    )
    return res.data || []
  }

  const fetchHolidays = async (year: number): Promise<HolidayItem[]> => {
    const res = await apiFetch<{ status: string; data: HolidayItem[] }>(
      `${baseURL}/features/pm-calendar/holidays?year=${year}`
    )
    return res.data || []
  }

  const fetchSites = async (): Promise<SiteOption[]> => {
    const res = await apiFetch<{ status: string; data: SiteOption[] }>(
      `${baseURL}/features/pm-calendar/sites`
    )
    return res.data || []
  }

  const fetchDepartments = async (site?: string): Promise<DepartmentOption[]> => {
    const url = site
      ? `${baseURL}/features/pm-calendar/departments?site=${site}`
      : `${baseURL}/features/pm-calendar/departments`
    const res = await apiFetch<{ status: string; data: DepartmentOption[] }>(url)
    return res.data || []
  }

  return {
    fetchTasks,
    fetchWorkOrderActivities,
    fetchTask,
    fetchWorkOrderActivity,
    createTask,
    updateTask,
    rescheduleTask,
    updateTaskStatus,
    deleteTask,
    fetchActivities,
    fetchLabor,
    fetchTimeSlots,
    fetchHolidays,
    fetchSites,
    fetchDepartments,
  }
}
