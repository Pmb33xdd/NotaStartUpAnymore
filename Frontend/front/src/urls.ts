export const BASE_URL = import.meta.env.VITE_BASE_URL || 'https://www.google.com/';
export const DATOS_DE_USUARIO_URL = `${BASE_URL}/me`;
export const ENVIAR_CORREO_CONTACTANOS_URL = `${BASE_URL}/contactmail`;
export const LOGIN_URL = `${BASE_URL}/login`;
export const FILTROS_URL = `${BASE_URL}/me/filters`;
export const NEWS_URL = `${BASE_URL}/news`;
export const COMPANIES_URL = `${BASE_URL}/companies`;
export const REGISTER_URL = `${BASE_URL}/`;
export const FILTROS_FETCH_URL = `${BASE_URL}/filters`;
export const DATOS_GRAFICOS_URL = (params: Record<string, string>) => {
    const urlParams = new URLSearchParams(params).toString();
    return `${BASE_URL}/charts?${urlParams}`;
};
export const API_KEY = import.meta.env.VITE_API_KEY || 'sfjicisjndjkanjdñflffkewjlkrkfmclksklnk';
