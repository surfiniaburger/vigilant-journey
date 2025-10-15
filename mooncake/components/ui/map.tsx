'use client';

import React, { useEffect, useRef } from 'react';

const Map = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const scriptLoaded = useRef(false);

  useEffect(() => {
    const loadGoogleMapsScript = () => {
      if (scriptLoaded.current) {
        (window as any).initMap();
        return;
      }
      
      scriptLoaded.current = true;
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&v=beta&callback=initMap`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    };

    (window as any).initMap = async () => {
      const { Map3DElement } = await (window as any).google.maps.importLibrary('maps3d');
      if (mapRef.current) {
        // Clear the div before appending a new map
        while (mapRef.current.firstChild) {
          mapRef.current.removeChild(mapRef.current.firstChild);
        }
        
        const map = new Map3DElement({
          center: { lat: 37.7704, lng: -122.3985, altitude: 500 },
          tilt: 67.5,
          mode: 'HYBRID',
        });
        mapRef.current.appendChild(map);
      }
    };

    loadGoogleMapsScript();

  }, []);

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
};

export { Map };