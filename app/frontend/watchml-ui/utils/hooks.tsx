import { useEffect, useState } from "react";
import API from "./api";

export function useFetch(url: string) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  useEffect(() => {
    async function fetchAPI() {
      try {
        const data = await fetch(url);
        setData(await data.json());
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    }
    fetchAPI();
  }, [url]);
  return [data, error, loading] as const;
}

export function useUserkey() {
  const [userKey, setUserKey] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserKey = async () => {
      const storedUserKey = localStorage.getItem("userKey");
      if (storedUserKey) {
        setUserKey(storedUserKey);
      } else {
        const fetchedUserKey = await fetch(API.getUserkey()).then((res) => res.text());
        if (fetchedUserKey) {
          localStorage.setItem("userKey", fetchedUserKey);
          setUserKey(fetchedUserKey);
        }
      }
    };

    fetchUserKey();
  }, []);

  return [userKey, null, false] as const;
}
