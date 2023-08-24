import "package:aw40_hub_frontend/env/env.dart";
import "package:aw40_hub_frontend/exceptions/exceptions.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:logging/logging.dart";

class ConfigService {
  factory ConfigService() => _configService;
  ConfigService._singleton();
  static final ConfigService _configService = ConfigService._singleton();

  final Logger _logger = Logger("config_service");
  Map<ConfigKey, String> configMap = {};
  bool _initialized = false;

  Future<void> initialize() async {
    await _importConfigValues();
    _initialized = true;
  }

  Future<void> _importConfigValues() async {
    configMap[ConfigKey.logLevel] = Env.logLevel;
    configMap[ConfigKey.backendUrl] = Env.backendUrl;
    configMap[ConfigKey.basicAuthKey] = Env.basicAuthKey;
    configMap[ConfigKey.kcClient] = Env.kcClient;
    configMap[ConfigKey.kcBaseUrl] = Env.kcBaseUrl;
    configMap[ConfigKey.kcRealm] = Env.kcRealm;
    configMap[ConfigKey.rootDomain] = Env.rootDomain;
    configMap[ConfigKey.redirectUriMobile] = Env.redirectUriMobile;
    if (EnvironmentService().hostPlatform == HostPlatform.android) {
      for (final key in ConfigKey.values) {
        final String value = configMap[key]!;
        if (value.contains("localhost")) {
          configMap[key] = _androidifyUrl(value);
        }
      }
    }
  }

  String getConfigValue(ConfigKey configKey) {
    _ensureInitDone();
    final String? configValue = configMap[configKey];
    if (configValue == null) {
      throw AppException(
        exceptionMessage: "ConfigService getConfigValue: "
            "no value found for config with key: $configKey",
        exceptionType: ExceptionType.notFound,
      );
    }
    return configValue;
  }

  void _ensureInitDone() {
    if (!_initialized) {
      throw AppException(
        exceptionType: ExceptionType.other,
        exceptionMessage: "Called ConfigService method before init was done.",
      );
    }
  }

  /// Replaces `localhost` with `10.0.2.2`. On Android, `localhost` refers to
  /// the emulator itself, `10.0.2.2` refers to the webbrowser within the
  /// Android app.
  String _androidifyUrl(String oldUrl) {
    final String newUrl = oldUrl.replaceFirst("localhost", "10.0.2.2");
    _logger.warning("Androidifying URL $oldUrl to $newUrl");
    return newUrl;
  }
}
