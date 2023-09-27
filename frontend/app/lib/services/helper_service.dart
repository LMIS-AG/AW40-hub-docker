import "package:aw40_hub_frontend/exceptions/exceptions.dart";
import "package:aw40_hub_frontend/main.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:flutter/widgets.dart";
import "package:logging/logging.dart";

class HelperService {
  static Level? getLogLevelFromConfigMap() {
    final String logLevelValueFromConfigMap =
        ConfigService().getConfigValue(ConfigKey.logLevel);
    return HelperService._stringToLogLevel(logLevelValueFromConfigMap);
  }

  static Level? _stringToLogLevel(String s) {
    final String ss = s.toLowerCase();
    if (ss == "all") return Level.ALL;
    if (ss == "finest") return Level.FINEST;
    if (ss == "finer") return Level.FINER;
    if (ss == "fine") return Level.FINE;
    if (ss == "config") return Level.CONFIG;
    if (ss == "info") return Level.INFO;
    if (ss == "warning") return Level.WARNING;
    if (ss == "severe") return Level.SEVERE;
    if (ss == "shout") return Level.SHOUT;
    if (ss == "off") return Level.OFF;
    return null;
  }

  static BuildContext get globalContext {
    final BuildContext? context = globalNavKey.currentContext;
    if (context == null) {
      throw AppException(
        exceptionType: ExceptionType.notFound,
        exceptionMessage: "context from globalNavKey was null",
      );
    }
    return context;
  }

  static DateTime? awFormatToDateTime(String awDateString) {
    // 2023-05-17T10:52:26.149000
    final List<int> intList = awDateString
        .replaceAll(RegExp("[:T.]"), "-")
        .split("-")
        .map(int.parse)
        .toList();
    if (intList.length != 7) {
      Logger("helper_service").warning(
        "Extracted ${intList.length} elements from AW date string. Expected 7. "
        "AW String was: $awDateString, extracted ints were $intList",
      );
      return null;
    }
    return DateTime(
      intList[0],
      intList[1],
      intList[2],
      intList[3],
      intList[4],
      intList[5],
      intList[6],
    );
  }
}
