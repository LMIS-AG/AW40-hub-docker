import "package:aw40_hub_frontend/data_sources/diagnosis_data_table_source.dart";
import "package:aw40_hub_frontend/exceptions/exceptions.dart";
import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class DiagnosisView extends StatelessWidget {
  const DiagnosisView({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final diagnosisProvider = Provider.of<DiagnosisProvider>(context);
    return FutureBuilder(
      // ignore: discarded_futures
      future: diagnosisProvider.getDiagnoses(
          ["ABC123", "XYZ789", "DEF456"]), // TODO replace mock data
      builder:
          (BuildContext context, AsyncSnapshot<List<DiagnosisModel>> snapshot) {
        if (snapshot.connectionState == ConnectionState.done &&
            snapshot.hasData) {
          final List<DiagnosisModel>? diagnosisModels = snapshot.data;
          if (diagnosisModels == null) {
            throw AppException(
              exceptionType: ExceptionType.notFound,
              exceptionMessage: "Received no diagnosis data.",
            );
          }
          return DesktopDiagnosisView(
            diagnosisModels: diagnosisModels,
          );
        } else {
          return const Center(child: CircularProgressIndicator());
        }
      },
    );
  }
}

class DesktopDiagnosisView extends StatefulWidget {
  const DesktopDiagnosisView({required this.diagnosisModels, super.key});

  final List<DiagnosisModel> diagnosisModels;

  @override
  State<DesktopDiagnosisView> createState() => _DesktopDiagnosisViewState();
}

class _DesktopDiagnosisViewState extends State<DesktopDiagnosisView> {
  int? currentCaseIndex; // TODO rename

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          flex: 3,
          child: SingleChildScrollView(
            child: PaginatedDataTable(
              source: DiagnosisDataTableSource(
                diagnosisModels: widget.diagnosisModels,
                onPressedRow: (int i) => setState(() => currentCaseIndex = i),
              ),
              showCheckboxColumn: false,
              rowsPerPage: 50,
              columns: [
                DataColumn(label: Text(tr("general.status"))),
                DataColumn(label: Text(tr("general.case"))),
                DataColumn(label: Text(tr("general.date")), numeric: true),
              ],
            ),
          ),
        ),
        // TODO implement detail view
        /*
        if (currentCaseIndex != null)
          Expanded(
            flex: 2,
            child: DiagnosisDetailView(
              diagnosisModel: widget.diagnosisModels[currentCaseIndex!],
              onClose: () => setState(() => currentCaseIndex = null),
            ),
          )*/
      ],
    );
  }
}
