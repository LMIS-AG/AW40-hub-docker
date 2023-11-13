import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";

class DiagnosisView extends StatelessWidget {
  const DiagnosisView({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    // TODO create analog view to cases view
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(tr("diagnosis.title")),
        ],
      ),
    );
  }
}
