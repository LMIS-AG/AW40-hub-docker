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
  String toGermanDateTimeString() => "$day.$month.$year, $hour:$minute Uhr";
}

extension StringExtension on String {
  DateTime? toDateTime() {
    try {
      final parts = split(",");
      if (parts.length == 2) {
        final dateParts = parts[0].split(".");

        String timePart = parts[1].substring(1, parts[1].length - 4);
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
    } catch (e) {
      throw FormatException('Invalid format of the German DateTime string');
    }
    return null;
  }
}
