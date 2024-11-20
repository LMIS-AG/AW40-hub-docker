class AssetDefinitionModel {
  AssetDefinitionModel({
    required this.vin,
    required this.obdDataDtc,
    required this.timeseriesDataComponent,
  });

  String? vin;
  String? obdDataDtc;
  String? timeseriesDataComponent;

  Map<String, dynamic> toJson() {
    return {
      "vin": vin,
      "obdDataDtc": obdDataDtc,
      "timeseriesDataComponent": timeseriesDataComponent,
    };
  }
}
