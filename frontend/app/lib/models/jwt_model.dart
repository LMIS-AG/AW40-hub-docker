// ignore_for_file: avoid_dynamic_calls
import "package:aw40_hub_frontend/services/token_service.dart";

class JwtModel {
  JwtModel({
    required this.jwt,
    required this.exp,
    required this.groups,
    this.iat,
    this.authTime,
    this.jti,
    this.iss,
    this.typ,
    this.azp,
    this.sessionState,
    this.acr,
    this.scope,
    this.emailVerified,
    this.name,
    this.preferredUsername,
    this.givenName,
    this.familyName,
    this.email,
    this.locale,
  });

  factory JwtModel.fromJwtString(String jwt) {
    DateTime exp;
    List<String> groups;
    dynamic jsonData;
    jsonData = TokenService().decodeBodyFromJWT(jwt);
    exp = DateTime.fromMillisecondsSinceEpoch(jsonData["exp"] * 1000 as int);
    groups = jsonData?["groups"].cast<String>() as List<String>? ?? [];

    return JwtModel(
      jwt: jwt,
      exp: exp,
      groups: groups,
      iat: jsonData != null
          ? DateTime.fromMillisecondsSinceEpoch(jsonData["iat"] * 1000 as int)
          : null,
      authTime: jsonData != null
          ? DateTime.fromMillisecondsSinceEpoch(
              jsonData["auth_time"] * 1000 as int,
            )
          : null,
      jti: jsonData?["jti"] as String?,
      iss: jsonData?["iss"] as String?,
      typ: jsonData?["typ"] as String?,
      azp: jsonData?["azp"] as String?,
      sessionState: jsonData?["session_state"] as String?,
      acr: jsonData?["acr"] as String?,
      scope: jsonData?["scope"] as String?,
      emailVerified: jsonData?["email_verified"] as bool?,
      name: jsonData?["name"] as String?,
      preferredUsername: jsonData?["preferred_username"] as String?,
      givenName: jsonData?["given_name"] as String?,
      familyName: jsonData?["family_name"] as String?,
      email: jsonData?["email"] as String?,
      locale: jsonData?["locale"] as String?,
    );
  }
  String jwt;
  DateTime exp;
  List<String> groups;
  DateTime? iat;
  DateTime? authTime;
  String? jti;
  String? iss;
  String? typ;
  String? azp;
  String? sessionState;
  String? acr;
  String? scope;
  bool? emailVerified;
  String? name;
  String? preferredUsername;
  String? givenName;
  String? familyName;
  String? email;
  String? locale;
}
