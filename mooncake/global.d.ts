// global.d.ts
declare namespace google.maps {
  function importLibrary<T = unknown>(library: string): Promise<T>
}

declare module 'google.maps.maps3d' {
  export const Marker3DInteractiveElement: new (options: {
    position: google.maps.LatLngLiteral
    extruded: boolean
    drawsWhenOccluded: boolean
    altitudeMode: string
  }) => HTMLElement

  export const AltitudeMode: {
    RELATIVE_TO_MESH: string
  }
}
