plugins {
    `java-library`
    id("application")
    id("com.github.johnrengelman.shadow") version "7.1.2"
}

val groupId: String by project
val edcVersion: String by project

dependencies {
    implementation("$groupId:core-spi:$edcVersion")
    implementation("$groupId:json-ld:$edcVersion")
    implementation("$groupId:json-ld-spi:$edcVersion")
    implementation("$groupId:management-api-configuration:$edcVersion")
    implementation("$groupId:dsp-transform:$edcVersion")
    implementation("$groupId:util:$edcVersion")
    implementation("$groupId:connector-core:$edcVersion")
    implementation("$groupId:runtime-metamodel:$edcVersion")
    implementation("$groupId:catalog-spi:$edcVersion")
    implementation("$groupId:web-spi:$edcVersion")
    implementation("$groupId:federated-catalog-core:$edcVersion")
    implementation("$groupId:federated-catalog-api:$edcVersion")
    implementation("$groupId:federated-catalog-spi:$edcVersion")

    implementation("org.springframework.boot:spring-boot-starter-web:3.1.2")

}

application {
    mainClass.set("org.eclipse.edc.boot.system.runtime.BaseRuntime")
}

tasks.withType<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar> {
    exclude("**/pom.properties", "**/pom.xm")
    mergeServiceFiles()
    archiveFileName.set("node-directoy.jar")
}
