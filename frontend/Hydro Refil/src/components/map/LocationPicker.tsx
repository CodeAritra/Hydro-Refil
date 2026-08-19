import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Navigation, MapPin, Search, Crosshair, Sparkles } from 'lucide-react';
import rainfallData from '../../data/rainfall-india.json';

// Fix default Leaflet icon path issues in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface LocationPickerProps {
  latitude: number;
  longitude: number;
  address?: string;
  district?: string;
  state?: string;
  onChange: (loc: { latitude: number; longitude: number; address?: string; district?: string; state?: string; rainfall_mm?: number }) => void;
}

function MapClickHandler({ onLocationSelect }: { onLocationSelect: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function MapCenterUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

export const LocationPicker: React.FC<LocationPickerProps> = ({
  latitude,
  longitude,
  address,
  district,
  state,
  onChange,
}) => {
  const [position, setPosition] = useState<[number, number]>([latitude || 22.5726, longitude || 88.3639]);
  const [selectedCityKey, setSelectedCityKey] = useState<string>('');
  const [isLocating, setIsLocating] = useState<boolean>(false);

  useEffect(() => {
    if (latitude && longitude) {
      setPosition([latitude, longitude]);
    }
  }, [latitude, longitude]);

  const handleMapClick = (lat: number, lng: number) => {
    setPosition([lat, lng]);
    onChange({
      latitude: Number(lat.toFixed(5)),
      longitude: Number(lng.toFixed(5)),
      address: address || `Coordinates: ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E`,
      district,
      state,
    });
  };

  const handleCityPresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedCityKey(val);
    if (!val) return;
    const match = rainfallData.find((item) => `${item.state}_${item.district}` === val);
    if (match) {
      setPosition([match.lat, match.lng]);
      onChange({
        latitude: match.lat,
        longitude: match.lng,
        district: match.district,
        state: match.state,
        address: `${match.district}, ${match.state}`,
        rainfall_mm: match.annual_rainfall_mm,
      });
    }
  };

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsLocating(false);
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setPosition([lat, lng]);
        onChange({
          latitude: Number(lat.toFixed(5)),
          longitude: Number(lng.toFixed(5)),
          address: 'Field GPS Position Recorded',
        });
      },
      (err) => {
        setIsLocating(false);
        alert(`GPS location error: ${err.message}. Please click manually on the map.`);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  return (
    <div className="space-y-4">
      {/* Top Toolbar / Presets */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="flex-1 relative">
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            Quick Select Indian District (IMD Normal Lookup)
          </label>
          <select
            value={selectedCityKey}
            onChange={handleCityPresetChange}
            className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
          >
            <option value="">-- Choose Indian District to Auto-Fill Rainfall --</option>
            {rainfallData.map((item) => (
              <option key={`${item.state}_${item.district}`} value={`${item.state}_${item.district}`}>
                {item.district} ({item.state}) — {item.annual_rainfall_mm} mm/yr
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={handleGetCurrentLocation}
          disabled={isLocating}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-sky-300 border border-slate-700 rounded-lg text-sm font-medium transition-colors sm:self-end h-[38px]"
        >
          <Crosshair className={`w-4 h-4 ${isLocating ? 'animate-spin' : ''}`} />
          {isLocating ? 'Acquiring GPS...' : 'Use Current Location'}
        </button>
      </div>

      {/* Interactive Map Box */}
      <div className="relative h-72 sm:h-80 w-full rounded-xl overflow-hidden border border-slate-700 shadow-inner">
        <MapContainer
          center={position}
          zoom={13}
          scrollWheelZoom={false}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={position} />
          <MapClickHandler onLocationSelect={handleMapClick} />
          <MapCenterUpdater center={position} />
        </MapContainer>

        {/* Overlay instruction */}
        <div className="absolute bottom-2 left-2 z-[400] bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-md border border-slate-700 text-xs text-slate-300 flex items-center gap-1.5 pointer-events-none shadow-md">
          <MapPin className="w-3.5 h-3.5 text-sky-400 flex-shrink-0" />
          <span>Click anywhere on the map to pin exact site coordinates</span>
        </div>
      </div>

      {/* Coordinate Display */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
          <span className="text-slate-400 block font-medium">Latitude</span>
          <span className="text-slate-100 font-mono font-semibold text-sm">{position[0].toFixed(5)}° N</span>
        </div>
        <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
          <span className="text-slate-400 block font-medium">Longitude</span>
          <span className="text-slate-100 font-mono font-semibold text-sm">{position[1].toFixed(5)}° E</span>
        </div>
        <div className="col-span-2 bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60 flex items-center justify-between">
          <div>
            <span className="text-slate-400 block font-medium">Location Summary</span>
            <span className="text-slate-200 truncate block font-medium">
              {district ? `${district}, ${state || 'India'}` : (address || 'Custom Coordinates')}
            </span>
          </div>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            GIS Ready
          </span>
        </div>
      </div>
    </div>
  );
};
