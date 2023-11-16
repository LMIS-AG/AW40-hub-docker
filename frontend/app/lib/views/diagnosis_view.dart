import "package:aw40_hub_frontend/data_sources/diagnosis_data_table_source.dart";
import "package:aw40_hub_frontend/exceptions/exceptions.dart";
import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:aw40_hub_frontend/views/diagnosis_detail_view.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";
import "package:routemaster/routemaster.dart";

class DiagnosisView extends StatelessWidget {
  const DiagnosisView({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final pathParameters = Routemaster.of(context).currentRoute.pathParameters;
    final String? diagnosisIdString = pathParameters["diagnosisId"];
    final int? diagnosisId =
        diagnosisIdString != null ? int.tryParse(diagnosisIdString) : null;

    final diagnosisProvider = Provider.of<DiagnosisProvider>(context);
    return FutureBuilder(
      // ignore: discarded_futures
      future: diagnosisProvider.getDiagnoses(
        ["ABC123", "XYZ789", "DEF456"],
      ), // TODO replace mock data
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
          diagnosisModels.sort((a, b) => a.status.index - b.status.index);
          return DesktopDiagnosisView(
            diagnosisModels: diagnosisModels,
            diagnosisId: diagnosisId,
          );
        } else {
          return const Center(child: CircularProgressIndicator());
        }
      },
    );
  }
}

class DesktopDiagnosisView extends StatefulWidget {
  const DesktopDiagnosisView(
      {required this.diagnosisModels, this.diagnosisId, super.key});

  final List<DiagnosisModel> diagnosisModels;
  final int? diagnosisId;

  @override
  State<DesktopDiagnosisView> createState() => _DesktopDiagnosisViewState();
}

class _DesktopDiagnosisViewState extends State<DesktopDiagnosisView> {
  int? currentDiagnosisIndex = -1;

  @override
  Widget build(BuildContext context) {
    if (currentDiagnosisIndex == -1) {
      currentDiagnosisIndex = widget.diagnosisId ?? 0;
    }
    return Row(
      children: [
        Expanded(
          flex: 3,
          child: SingleChildScrollView(
            child: PaginatedDataTable(
              source: DiagnosisDataTableSource(
                diagnosisModels: widget.diagnosisModels,
                onPressedRow: (int i) =>
                    setState(() => currentDiagnosisIndex = i),
              ),
              showCheckboxColumn: false,
              rowsPerPage: 50,
              columns: [
                DataColumn(
                  label: Expanded(
                    child: Center(child: Text(tr("general.id"))),
                  ),
                ),
                DataColumn(
                  label: Expanded(
                    child: Center(child: Text(tr("general.status"))),
                  ),
                ),
                DataColumn(
                  label: Expanded(
                    child: Center(child: Text(tr("general.case"))),
                  ),
                ),
                DataColumn(
                  label: Expanded(
                    child: Center(child: Text(tr("general.date"))),
                  ),
                  numeric: true,
                ),
              ],
            ),
          ),
        ),
        if (currentDiagnosisIndex != null)
          Expanded(
            flex: 2,
            child: DiagnosisDetailView(
              diagnosisModel: widget.diagnosisModels[currentDiagnosisIndex!],
            ),
          )
      ],
    );
  }
}
