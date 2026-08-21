import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { LandslideEvent } from '@/types';

interface MapPreviewProps {
  events: LandslideEvent[];
  height?: string | number;
  onEventClick?: (event: LandslideEvent) => void;
}

export const MapPreview: React.FC<MapPreviewProps> = ({
  events,
  height = 360,
  onEventClick,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) return;

    // Use free public OpenStreetMap / Carto dark style
    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: [
              'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
              'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            ],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
          },
        },
        layers: [
          {
            id: 'osm-layer',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [92.5, 26.0], // NER Centroid (Assam / Meghalaya)
      zoom: 6.0,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

    map.on('load', () => {
      // Add Verified Events GeoJSON Source
      const geojson: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: events.map((evt) => ({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [evt.longitude, evt.latitude],
          },
          properties: {
            event_id: evt.event_id,
            location_name: evt.location_name,
            state: evt.state,
            event_date: evt.event_date,
            source: evt.source,
          },
        })),
      };

      map.addSource('verified-events', {
        type: 'geojson',
        data: geojson,
      });

      // Event points outer glow
      map.addLayer({
        id: 'events-glow',
        type: 'circle',
        source: 'verified-events',
        paint: {
          'circle-radius': 8,
          'circle-color': '#f97316',
          'circle-opacity': 0.35,
        },
      });

      // Event points center
      map.addLayer({
        id: 'events-point',
        type: 'circle',
        source: 'verified-events',
        paint: {
          'circle-radius': 4.5,
          'circle-color': '#ea580c',
          'circle-stroke-width': 1.5,
          'circle-stroke-color': '#ffffff',
        },
      });

      // Click handler
      map.on('click', 'events-point', (e) => {
        if (!e.features || !e.features[0]) return;
        const props = e.features[0].properties;
        const coordinates = (e.features[0].geometry as any).coordinates.slice();

        new maplibregl.Popup({ offset: 10 })
          .setLngLat(coordinates)
          .setHTML(
            `<div style="font-size: 11px; line-height: 1.4;">
              <strong style="color: #ea580c; font-size: 12px; display: block; margin-bottom: 2px;">${props?.location_name || 'Landslide Event'}</strong>
              <div><b>State:</b> ${props?.state}</div>
              <div><b>Date:</b> ${props?.event_date}</div>
              <div><b>Source:</b> ${props?.source}</div>
              <div style="margin-top: 4px; color: #38bdf8; font-weight: 600;">Status: VERIFIED HISTORICAL</div>
            </div>`
          )
          .addTo(map);

        const matched = events.find((ev) => ev.event_id === props?.event_id);
        if (matched && onEventClick) onEventClick(matched);
      });

      // Cursor pointer
      map.on('mouseenter', 'events-point', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'events-point', () => {
        map.getCanvas().style.cursor = '';
      });
    });

    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, [events, onEventClick]);

  return (
    <div
      ref={mapContainer}
      className="w-full rounded-lg overflow-hidden border border-slate-800 shadow-inner bg-slate-950"
      style={{ height }}
    />
  );
};
