import type { CoverageNetwork } from '~/types/coverage'

/** Presentation only: column ranks and coordinates, never coverage or route results. */
export function layoutNetwork(network: CoverageNetwork) {
  const nodes = [...network.nodes].sort((a, b) => a.id - b.id)
  const ids = new Set(nodes.map((node) => node.id))
  const links = network.connections.flatMap((connection) => {
    const from = connection.origin.id
    const to = connection.destination.id
    if (!ids.has(from) || !ids.has(to)) return []
    return connection.is_bidirectional
      ? [
          [from, to],
          [to, from],
        ]
      : [[from, to]]
  })
  const ranks = new Map<number, number>()
  const positions = new Map<number, { x: number; y: number }>()
  nodes
    .filter((node) => node.type === 'BASE')
    .forEach((node) => ranks.set(node.id, 0))

  function assignColumns() {
    // Snapshot each pass so input order cannot change the visual ranks. Cycles
    // stop at an assigned rank; they cannot grow the layout indefinitely.
    for (let pass = 0; pass < nodes.length; pass++) {
      const previous = new Map(ranks)
      const candidates = new Map<number, number>()
      for (const [from, to] of links) {
        const rank = previous.get(from!)
        if (rank === undefined || previous.has(to!)) continue
        candidates.set(to!, Math.min(candidates.get(to!) ?? Infinity, rank + 1))
      }
      if (!candidates.size) break
      candidates.forEach((rank, id) => ranks.set(id, rank))
    }
  }

  function placeGroup(groupIds: number[], top: number) {
    const columns = new Map<number, number[]>()
    for (const id of groupIds) {
      const rank = ranks.get(id) ?? 0
      const column = columns.get(rank) ?? []
      column.push(id)
      columns.set(rank, column)
    }
    const height =
      Math.max(1, ...[...columns.values()].map((column) => column.length)) * 116
    // Sort a column by the average position of already placed predecessors.
    for (const [rank, column] of [...columns].sort(([a], [b]) => a - b)) {
      const center = (id: number) => {
        const parents = links
          .filter(([from, to]) => to === id && positions.has(from!))
          .map(([from]) => positions.get(from!)!.y)
        return parents.length
          ? parents.reduce((sum, y) => sum + y, 0) / parents.length
          : top + height / 2
      }
      column.sort((a, b) => center(a) - center(b) || a - b)
      column.forEach((id, row) =>
        positions.set(id, {
          x: rank * 280,
          y: top + (height - column.length * 116) / 2 + row * 116,
        }),
      )
    }
    return height
  }

  assignColumns()
  let top = placeGroup(
    nodes.filter((node) => ranks.has(node.id)).map((node) => node.id),
    0,
  )
  // Components without an outgoing route from a base sit below the main network.
  // Seed a source where possible, or a stable ID for a closed directed cycle.
  while (ranks.size < nodes.length) {
    const remaining = nodes.filter((node) => !ranks.has(node.id))
    const root =
      remaining.find(
        (node) =>
          !links.some(([from, to]) => to === node.id && !ranks.has(from!)),
      ) ?? remaining[0]!
    const before = new Set(ranks.keys())
    ranks.set(root.id, 0)
    assignColumns()
    top += 48
    top += placeGroup(
      nodes
        .filter((node) => !before.has(node.id) && ranks.has(node.id))
        .map((node) => node.id),
      top,
    )
  }
  return positions
}
