export async function fetchPlus(url: string, options = {}, retries: number): Promise<any> {
  const response = await fetch(url, options);
  if (response.ok) {
    return await response.json();
  }
  if (retries > 0) {
    setTimeout(() => {}, 1000);
    return await fetchPlus(url, options, retries - 1);
  }
  throw new Error(response.statusText);
}
