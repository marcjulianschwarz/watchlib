// make it static

import { fetchPlus } from "./data";

//const baseURL = "http://127.0.0.1:5000";
const baseURL = "http://test.marc-julian.de"

export default class API {
  static getECGs(ukey: string) {
    return baseURL + "/api/ecgs/" + ukey;
  }

  static uploadECGAction(ukey: string) {
    return baseURL + "/api/upload/ecgs/" + ukey;
  }

  static getUserkey() {
    return baseURL + "/api/userkey";
  }
}
