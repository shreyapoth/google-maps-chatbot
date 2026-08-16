export default function MapView() {
  return (
    <section className="map" aria-label="Map preview">
      <div className="map-canvas" aria-hidden="true">
        <span className="map-road map-road-horizontal" />
        <span className="map-road map-road-vertical" />
        <span className="map-road map-road-diagonal" />
        <span className="map-water" />
        <span className="map-park" />
        <span className="map-marker" />
      </div>

      <div className="map-overlay">
        <p className="map-note">Map preview</p>
        <p className="map-hint">Connect the Google Maps JS API to draw real results here.</p>
      </div>

      <div className="map-controls" aria-hidden="true">
        <span className="map-control">+</span>
        <span className="map-control">−</span>
      </div>
    </section>
  );
}
