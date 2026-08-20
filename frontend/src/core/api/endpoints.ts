export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    me: '/auth/me',
    users: '/auth/users',
  },
  geography: {
    deaneries: '/geography/deaneries',
    parishes: '/geography/parishes',
    centrales: (parishId: string) => `/geography/parishes/${parishId}/centrales`,
    scc: (centraleId: string) => `/geography/centrales/${centraleId}/scc`,
  },
  faithful: {
    list: '/faithful',
    detail: (id: string) => `/faithful/${id}`,
    create: '/faithful',
    families: '/faithful/families',
  },
  sacraments: {
    baptism: '/sacraments/baptism',
    confirmation: '/sacraments/confirmation',
    matrimony: '/sacraments/matrimony',
    issueCertificate: '/sacraments/certificates/issue',
  },
  clergy: {
    list: '/clergy',
    detail: (id: string) => `/clergy/${id}`,
    create: '/clergy',
    assignments: '/clergy/assignments',
  },
  liturgy: {
    masses: '/liturgy/masses',
    intentions: '/liturgy/intentions',
  },
  finance: {
    donations: '/finance/donations',
    summary: '/finance/summary',
  },
  ministries: {
    list: '/ministries',
    create: '/ministries',
  },
  landAssets: {
    parcels: '/land-assets/parcels',
    parcelDetail: (id: string) => `/land-assets/parcels/${id}`,
    buildings: '/land-assets/buildings',
  },
  archive: {
    books: '/archive/books',
    pages: (bookId: string) => `/archive/books/${bookId}/pages`,
  },
  statistics: {
    parishReports: '/statistics/parish-reports',
    annuarioPontificio: '/statistics/annuario-pontificio',
  },
};
