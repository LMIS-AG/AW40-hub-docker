import "package:aw40_hub_frontend/models/costumer_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:json_annotation/json_annotation.dart";

part "costumer_dto.g.dart";

@JsonSerializable()
class CostumerDto {
  CostumerDto(
    this.id,
  );

  factory CostumerDto.fromJson(Map<String, dynamic> json) {
    return _$CostumerDtoFromJson(json);
  }
  Map<String, dynamic> toJson() => _$CostumerDtoToJson(this);

  CostumerModel toModel() {
    return CostumerModel(
      id: id,
    );
  }

  @JsonKey(name: "_id")
  AnonymousCustomerId id;
}
