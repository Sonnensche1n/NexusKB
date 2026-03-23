export const flow_node_shape = 'flow-node'

export const portAttrs = {
  circle: {
    magnet: true,
    r: 5,
    stroke: 'var(--primary-color)',
    fill: 'var(--base-color)',
    strokeWidth: 2,
  }
}

export const portGroups = {
  incoming: {
    position: 'left',
    attrs: portAttrs
  },
  incoming2: {
    position: {
      name: 'absolute',
      args: { x: 0, y: 0 },
    },
    attrs: portAttrs
  },
  outgoing: {
    position: 'right',
    attrs: portAttrs
  },
  outgoing2: {
    position: {
      name: 'absolute',
      args: { x: '100%', y: 0 },
    },
    attrs: portAttrs
  }
}
export const createGraphNode = (nodeData) => {
  let ports = nodeData['ports']
  let portItems = []
  ports.forEach(port => {
    let portTyp = port['portTyp']
    let attrVal = port['valKey']
    portItems.push({
      group: portTyp + (Boolean(attrVal) ? '2' : ''),
      id: port['portId'],
      args: {
        y: port['posY'],
      },
      data: port
    })
  })
  return {
    id: nodeData['nodeId'],
    shape: flow_node_shape,
    x: nodeData['posX'] || 0,
    y: nodeData['posY'] || 0,
    width: nodeData['width'] || 300,
    height: 60,
    data: nodeData,
    ports: {
      groups: portGroups,
      items: portItems
    }
  }
}

export const createGraphEdge = (edgeData, nodeMap) => {
  let srcId = edgeData['srcId']
  let tgtId = edgeData['tgtId']
  let srcPortId = edgeData['srcPortId']
  let tgtPortId = edgeData['tgtPortId']
  if (nodeMap) {
    if (!nodeMap[srcId] || !nodeMap[tgtId]) {
      return
    }
  }
  return {
    id: edgeData['edgeId'],
    source: { cell: srcId, port: srcPortId }, // 源节点和连接桩 ID
    target: { cell: tgtId, port: tgtPortId }, // 目标节点 ID 和连接桩 ID
    data: edgeData,
    connector: {
      name: 'smooth',
      args: {},
    },
    attrs: {
      line: {
        stroke: 'var(--primary-color)',
      }
    }
  }
}

/**
 * 获取子元素到父元素偏移
 * @param {*} element 
 * @param {*} parent 
 * @returns 
 */
export const getElementOffset = (element, parent) => {
  let top = 0, left = 0
  while (element && element !== parent) {
    top += element.offsetTop || 0
    left += element.offsetLeft || 0
    element = element.offsetParent
  }
  return { top, left }
}