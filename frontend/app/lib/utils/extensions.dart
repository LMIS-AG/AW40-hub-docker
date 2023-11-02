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
