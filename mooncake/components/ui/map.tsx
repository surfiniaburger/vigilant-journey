'use client';

import React, { useEffect, useRef } from 'react';
import { Loader } from '@googlemaps/js-api-loader';

const Map = () => {
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loader = new Loader({
      apiKey: 'YOUR_API_KEY', // IMPORTANT: Replace with your API key
      version: 'beta',
      libraries: ['maps3d'],
    });

    loader.load().then(async () => {
      const { Map3DElement } = await google.maps.importLibrary('maps3d');

      if (mapRef.current) {
        const map = new Map3DElement({
          center: { lat: 37.7704, lng: -122.3985, altitude: 500 },
          tilt: 67.5,
          mode: 'HYBRID',
        });

        mapRef.current.appendChild(map);
      }
    });
  }, []);

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
};

export { Map };
