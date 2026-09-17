export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    me: '/auth/me',
    users: '/auth/users',
    forgotPassword: '/auth/forgot-password',
    resetPassword: '/auth/reset-password',
  },
  geography: {
    deaneries: '/geography/deaneries',
    parishes: '/geography/parishes',
    parishDetail: (parishId: string) => `/geography/parishes/${parishId}`,
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
    list: '/clergy/priests',
    detail: (id: string) => `/clergy/priests/${id}`,
    create: '/clergy/priests',
    assignments: '/clergy/assignments',
  },
  liturgy: {
    masses: '/liturgy/mass-schedules',
    intentions: '/liturgy/intentions',
    intentionDetail: (id: string) => `/liturgy/intentions/${id}`,
  },
  finance: {
    donations: '/finance/donations',
    donationDetail: (id: string) => `/finance/donations/${id}`,
    summary: '/finance/summary',
  },
  ministries: {
    list: '/ministries/',
    create: '/ministries/',
  },
  landAssets: {
    parcels: '/land-assets/parcels',
    parcelDetail: (id: string) => `/land-assets/parcels/${id}`,
    buildings: '/land-assets/buildings',
    parcelBuildings: (parcelId: string) => `/land-assets/parcels/${parcelId}/buildings`,
  },
  archive: {
    books: '/archive/books',
    pages: (bookId: string) => `/archive/books/${bookId}/pages`,
    createPage: '/archive/pages',
    pageDetail: (pageId: string) => `/archive/pages/${pageId}`,
    triggerOcr: (pageId: string) => `/archive/pages/${pageId}/ocr`,
    searchPages: '/archive/pages/search',
  },
  statistics: {
    parishReports: '/statistics/parish-reports',
    submitReport: '/statistics/parish-report',
    annuarioPontificio: '/statistics/annuario-pontificio',
    indicators: '/statistics/indicators',
    computeIndicator: (key: string) => `/statistics/indicators/${key}`,
  },
};

