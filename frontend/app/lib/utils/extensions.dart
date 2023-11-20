import "package:flutter/widgets.dart";

extension SetStateIfMountedExtension on State {
  void setStateIfMounted(void Function() method) {
    if (mounted) {
      // ignore: invalid_use_of_protected_member
      setState(method);
    }
  }
}

extension DateExtension on DateTime {
  String toGermanDateString() => "$day.$month.$year";
}

extension DateTimeExtension on DateTime {
  // ignore: lines_longer_than_80_chars
  String toGermanDateTimeString() =>
      "$day.$month.$year, ${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')} Uhr";
}

extension StringExtension on String {
  DateTime? toDateTime() {
    try {
      final parts = split(",");
      if (parts.length == 2) {
        final dateParts = parts[0].split(".");

        final String timePart = parts[1].substring(1, parts[1].length - 4);
        final timeParts = timePart.split(":");

        if (dateParts.length == 3 && timeParts.length == 2) {
          final day = int.parse(dateParts[0]);
          final month = int.parse(dateParts[1]);
          final year = int.parse(dateParts[2]);
          final hour = int.parse(timeParts[0]);
          final minute = int.parse(timeParts[1]);

          return DateTime(year, month, day, hour, minute);
        }
      }
    } on Exception {
      throw const FormatException(
        "Invalid format of the German DateTime string",
      );
    }
    return null;
  }
}
