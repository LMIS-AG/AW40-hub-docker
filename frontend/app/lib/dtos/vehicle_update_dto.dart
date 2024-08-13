import "package:json_annotation/json_annotation.dart";

part "vehicle_update_dto.g.dart";

// TODO maybe adjust this description
/// DTO for the PUT /{workshop_id}/vehicles/{case_id} endpoint.
@JsonSerializable()
class VehicleUpdateDto {
  VehicleUpdateDto(
    this.id,
    this.vin,
    this.tsn,
    this.yearBuild,
  );

  factory VehicleUpdateDto.fromJson(Map<String, dynamic> json) =>
      _$VehicleUpdateDtoFromJson(json);
  Map<String, dynamic> toJson() => _$VehicleUpdateDtoToJson(this);

  String? id;
  String? vin;
  String? tsn;
  int? yearBuild;
}
