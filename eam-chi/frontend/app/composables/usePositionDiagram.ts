import { useApi } from './useApi'
import { useApiFetch } from './useApiFetch'

type FilterOption = { label: string; value: string }

export const usePositionDiagram = () => {
  const { getPositionDiagram } = useApi()
  const { baseURL } = useApiFetch()
  const backendOrigin = baseURL.replace(/\/?api\/?$/, '')

  const toAbsoluteImageUrl = (url?: string | null) => {
    if (!url) return undefined
    if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
      return url
    }
    if (url.startsWith('/uploads/')) {
      return `${backendOrigin}${url}`
    }
    if (url.startsWith('/')) {
      return `${baseURL}${url}`
    }
    return `${baseURL}/${url}`
  }

  const loadDiagramData = async (filters: { location?: string; system?: string }) => {
    const response = await getPositionDiagram(filters)

    return {
      nodes: (response.nodes || []).map((node: any) => {
        const image = toAbsoluteImageUrl(node?.data?.image)

        return {
          ...node,
          data: {
            ...node.data,
            ...(image ? { image } : {}),
          },
        }
      }),
      edges: response.edges || [],
      locationOptions: (response.filters?.location || []) as FilterOption[],
      systemOptions: (response.filters?.system || []) as FilterOption[],
      selectedLocation: response.filters?.selected?.location || undefined,
      selectedSystem: response.filters?.selected?.system || undefined,
    }
  }

  return {
    loadDiagramData,
  }
}
