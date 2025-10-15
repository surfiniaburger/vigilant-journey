// Note: This component uses a manual script loading approach for the Google Maps API
// instead of a React-specific library (like @googlemaps/react-wrapper or the
// @googlemaps/js-api-loader library which we initially tried). This is because
// we encountered a persistent "Map3DElement is not a constructor" TypeError when
// using the loader library with the beta version of the Maps API for 3D maps.
//
// The current implementation directly mirrors the working vanilla JavaScript example
// provided by Google, which involves:
// 1. Dynamically creating a <script> tag to load the Google Maps API.
// 2. Using a promise-based approach to ensure the script is loaded before
//    initializing the map.
// 3. Programmatically creating the Map3DElement and appending it to the DOM.
//
// This approach, while more verbose, has proven to be the most reliable way to
// render the 3D map in this Next.js/React environment.
'use client';

import React, { useEffect, useRef } from 'react';

let scriptLoadingPromise: Promise<void> | null = null;

const loadGoogleMapsScript = () => {
  if (scriptLoadingPromise) {
    return scriptLoadingPromise;
  }

  scriptLoadingPromise = new Promise((resolve, reject) => {
    const scriptId = 'google-maps-script';
    if (document.getElementById(scriptId)) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.id = scriptId;
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&v=beta`;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = (error) => reject(error);
    document.head.appendChild(script);
  });

  return scriptLoadingPromise;
};

const Map = () => {
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let map: HTMLElement;
    const initMap = async () => {
      try {
        await loadGoogleMapsScript();
        const { Map3DElement } = await (window as any).google.maps.importLibrary('maps3d');
        if (mapRef.current) {
          map = new Map3DElement({
            center: { lat: 37.7704, lng: -122.3985, altitude: 500 },
            tilt: 67.5,
            mode: 'HYBRID',
          });
          mapRef.current.appendChild(map);
        }
      } catch (error) {
        console.error("Failed to load Google Maps script:", error);
      }
    };

    initMap();

    return () => {
      if (mapRef.current && map) {
        mapRef.current.removeChild(map);
      }
    };
  }, []);

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
};

export { Map };