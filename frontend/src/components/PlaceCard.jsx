export default function PlaceCard({ place }) {
  const address = place.formatted_address || place.address || "Address unavailable";
  const rating =
    place.rating == null ? "No rating" : `${place.rating} stars`;

  return (
    <article className="card">
      <strong>{place.name}</strong>
      <p>{address}</p>
      <span>{rating}</span>
    </article>
  );
}
