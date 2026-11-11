import type { Connection, RouteNode, RouteSegment } from '~/types/coverage'

/** Resolve an API path against real records, without finding a route locally. */
export function resolvePathSegments(
  path: RouteNode[],
  connections: Connection[],
): RouteSegment[] | null {
  if (!path.length) return null
  const segments: RouteSegment[] = []
  for (let index = 1; index < path.length; index++) {
    const origin = path[index - 1]!
    const destination = path[index]!
    const matches = connections.filter(
      (connection) =>
        (connection.origin.id === origin.id &&
          connection.destination.id === destination.id) ||
        (connection.is_bidirectional &&
          connection.origin.id === destination.id &&
          connection.destination.id === origin.id),
    )
    if (matches.length !== 1) return null
    const minutes = matches[0]!.estimated_minutes
    if (!Number.isFinite(minutes) || minutes <= 0) return null
    segments.push({ origin, destination, estimated_minutes: minutes })
  }
  return segments
}

export function compareRouteMinutes(
  bfsMinutes: number | null,
  dijkstraMinutes: number | null,
) {
  if (bfsMinutes === null || dijkstraMinutes === null) return null
  const difference = bfsMinutes - dijkstraMinutes
  return {
    difference,
    savingPercent: bfsMinutes > 0 ? (difference / bfsMinutes) * 100 : null,
  }
}
