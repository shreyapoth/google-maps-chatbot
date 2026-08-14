export default function PlaceCard({ place }) {
  const address = place.formatted_address || place.address || "Address unavailable";

  return (
    <article className="card">
      <strong>{place.name}</strong>
      <p>{address}</p>
    </article>
  );
}
