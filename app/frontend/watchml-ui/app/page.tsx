import Link from "next/link";
import styles from "./page.module.css";

function Card(props: { name: string }) {
  return (
    <Link href={"/" + props.name.toLowerCase()}>
      <div className={styles.card}>
        <p>{props.name}</p>
      </div>
    </Link>
  );
}

export default function Home() {
  return (
    <main className={styles.main}>
      <h1 className={styles.title}>WatchML</h1>
      <div className={styles.cards}>
        <Card name="ECG" />
        <Card name="Route" />
        <Card name="Other" />
      </div>
    </main>
  );
}
