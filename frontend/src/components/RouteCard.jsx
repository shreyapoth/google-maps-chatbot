export default function RouteCard({ route }) {
  return (
    <article className="card">
      <strong>Driving route</strong>
      <p>
        {route.distance_miles} mi · {route.duration_minutes} min
      </p>
    </article>
  );
}
