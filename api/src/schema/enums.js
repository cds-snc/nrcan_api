import { generateName } from '../utilities'

const tostr = Function.prototype.toString

function attachToString(func) {
  func.toString = function() {
    return `(${tostr.apply(func)})`
  }
  return func
}

// The fields on the dwelling type
const dwellingFields = [
  'houseId',
  'yearBuilt',
  'city',
  'region',
  'forwardSortationArea',
]

dwellingFields.forEach(attr => {
  // eslint-disable-next-line no-new-func
  let fn = new Function('matcher', `return { ${attr}: matcher }`)
  module.exports[generateName('dwelling', attr)] = attachToString(fn)
})

// The fields on the ventilation type
const ventilationFields = [
  'typeEnglish',
  'typeFrench',
  'airFlowRateLps',
  'airFlowRateCfm',
  'efficiency',
]

ventilationFields.forEach(attr => {
  // eslint-disable-next-line no-new-func
  let fn = new Function(
    'matcher',
    `
  return {
    evaluations: {
      $elemMatch: {
        ventilations: {
          $elemMatch:{ ${attr}: matcher },
        },
      },
    },
  }
  `,
  )
  module.exports[generateName('ventilation', attr)] = attachToString(fn)
})

// The fields on the floor type
const floorFields = [
  'label',
  'insulationNominalRsi',
  'insulationNominalR',
  'insulationEffectiveRsi',
  'insulationEffectiveR',
  'areaMetres',
  'areaFeet',
  'lengthMetres',
  'lengthFeet',
]

floorFields.forEach(attr => {
  // eslint-disable-next-line no-new-func
  let fn = new Function(
    'matcher',
    `
  return {
    evaluations: {
      $elemMatch: {
        floors: {
          $elemMatch:{ ${attr}: matcher },
        },
      },
    },
  }
  `,
  )
  module.exports[generateName('floor', attr)] = attachToString(fn)
})

// The fields on the WaterHeating type
const waterHeatingFields = [
  'typeEnglish',
  'typeFrench',
  'tankVolumeLitres',
  'tankVolumeGallon',
  'efficiency',
]

waterHeatingFields.forEach(attr => {
  // eslint-disable-next-line no-new-func
  let fn = new Function(
    'matcher',
    `
  return {
    evaluations: {
      $elemMatch: {
        waterHeatings: {
          $elemMatch:{ ${attr}: matcher },
        },
      },
    },
  }
  `,
  )
  module.exports[generateName('waterHeating', attr)] = attachToString(fn)
})
