/**
 * Attachment API Composable
 * =========================
 * Attachment CRUD for entity records.
 */
import { useApiFetch } from './useApiFetch'
import type { ActionResponse, AttachmentItem } from './useApiTypes'

export const useAttachmentApi = () => {
  const { apiFetch, baseURL } = useApiFetch()

  return {
    async getAttachments(entity: string, recordId: string): Promise<{ status: string; data: AttachmentItem[]; total: number }> {
      return apiFetch(`${baseURL}/entity/${entity}/${recordId}/attachments`)
    },

    async uploadAttachment(
      entity: string,
      recordId: string,
      file: File,
      description?: string
    ): Promise<ActionResponse<AttachmentItem>> {
      const form = new FormData()
      form.append('file', file)
      if (description) form.append('description', description)
      return apiFetch<ActionResponse<AttachmentItem>>(`${baseURL}/entity/${entity}/${recordId}/attachments`, { method: 'POST', body: form })
    },

    getAttachmentDownloadUrl(entity: string, recordId: string, attachmentId: string): string {
      return `${baseURL}/entity/${entity}/${recordId}/attachments/${attachmentId}/download`
    },

    async deleteAttachment(entity: string, recordId: string, attachmentId: string): Promise<ActionResponse> {
      return apiFetch<ActionResponse>(`${baseURL}/entity/${entity}/${recordId}/attachments/${attachmentId}`, { method: 'DELETE' })
    },
  }
}
