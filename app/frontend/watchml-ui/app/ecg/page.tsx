"use client";
import styles from "./page.module.css";
import { useState } from "react";

import { List } from "@/components/List/List";
import API from "../../utils/api";
import { useFetch, useUserkey } from "@/utils/hooks";

function ECGList(props: { userKey: string }) {
  const [ecgs, error, loading] = useFetch(API.getECGs(props.userKey));
  const [selected, setSelected] = useState<string>("");

  if (loading) {
    return <p>Loading...</p>;
  } else if (error) {
    return <p>Error</p>;
  } else if (!ecgs) {
    return <p>No ECGs found</p>;
  } else {
    const sel = ecgs.filter((ecg: ECG) => ecg.name === selected)[0];

    return (
      <div>
        {sel ? <p>{JSON.stringify(sel.values)}</p> : null}
        <List items={ecgs} selected={selected} onSelect={setSelected}></List>
      </div>
    );
  }
}

export default function ECGPage() {
  const [userKey, error, loading] = useUserkey();

  if (loading) {
    return <p>Loading...</p>;
  } else if (error) {
    return <p>Error</p>;
  } else if (!userKey) {
    return <p>No userKey found</p>;
  } else {
    return (
      <main className={styles.main}>
        <h1>ECG - for {userKey}</h1>
        <form action={API.uploadECGAction(userKey)} method="post" encType="multipart/form-data">
          <input type="file" name="file" />
          <input type="submit" value="Upload" />
        </form>
        <ECGList userKey={userKey} />
      </main>
    );
  }
}
