enum AuthorizedRole {
  analyst,
  mechanic,
}

enum ExceptionType {
  notFound,
  unexpectedNullValue,
  other,
  unknown,
}

enum HostPlatform {
  web,
  android,
  ios,
  windows,
  linux,
  macos,
}

enum TokenType {
  jwt,
  refresh,
  id,
}

enum ConfigKey {
  logLevel,
  backendUrl,
  basicAuthKey,
  kcClient,
  kcBaseUrl,
  kcRealm,
  rootDomain,
  redirectUriMobile,
}

enum LocalStorageKey {
  verifier,
  redirectUri,
  refreshToken,
}

enum CaseOccasion {
  unknown,
  // ignore: constant_identifier_names
  service_routine,
  // ignore: constant_identifier_names
  problem_defect,
}

enum CaseStatus {
  open,
  closed,
}

enum NavigationType {
  internal,
  external,
}
