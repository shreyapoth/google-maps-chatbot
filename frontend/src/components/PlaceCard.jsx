export default function PlaceCard({ place }) {
  return (
    <article className="card">
      <strong>{place.name}</strong>
      <p>{place.address}</p>
      <span>{place.rating} stars</span>
    </article>
  );
}
