package test

import (
	"fmt"
	"path/filepath"
	"strings"
	"testing"
	"text/template"

	"os"

	"github.com/gruntwork-io/terratest/modules/terraform"
	test_structure "github.com/gruntwork-io/terratest/modules/test-structure"
	"github.com/stretchr/testify/assert"
)

type ProviderConfig struct {
	ConfigPath string
	Context    string
}

const providerTemplate = `
provider "kubernetes" {
	config_path = "{{.ConfigPath}}"
	config_context = "{{.Context}}"
}
`
const rootDirectory string = "../../../../"
const rootOpenTofuDirectory string = "../../../../deployments/opentofu/modules"

func createKubernetesProviderFile(t *testing.T, config ProviderConfig, tempDirectory string) {
	// Validate template
	template, err := template.New("provider").Parse(providerTemplate)
	if err != nil {
		t.Fatalf("Failed to create template: %v", err)
	}

	destFile, err := os.Create(tempDirectory + "/__test_provider.tf")
	if err != nil {
		t.Fatalf("Failed to create destination file: %v", err)
	}
	defer destFile.Close()

	err = template.Execute(destFile, config)
	if err != nil {
		t.Fatalf("Failed to write template to file: %v", err)
	}

	// Sync to disk
	err = destFile.Sync()
	if err != nil {
		t.Fatalf("Failed to sync file: %v", err)
	}
}

func TestTerraformHelloWorldExample(t *testing.T) {
	t.Parallel()
	applicationNamespace := strings.ToLower(t.Name())
	applicationName := "hello-world"
	applicationImageRepository := fmt.Sprintf("localhost/%s", applicationName)
	applicationImageTag := "local-test"
	applicationFullImageName := fmt.Sprintf("%s:%s", applicationImageRepository, applicationImageTag)

	buildContainerImage(t, rootDirectory, "containers/python/Dockerfile", applicationFullImageName)

	err := loadPodmanImageToKindCluster(applicationFullImageName)
	assert.NoError(t, err)

	tempDirectory := test_structure.CopyTerraformFolderToTemp(t, rootOpenTofuDirectory, "kubernetes-deployment")
	kubeConfigPath, err := filepath.Abs(kindConfigPath)
	assert.NoError(t, err)
	provider := ProviderConfig{
		ConfigPath: kubeConfigPath,
		Context:    kindContext,
	}
	createKubernetesProviderFile(t, provider, tempDirectory)

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: tempDirectory,
		NoColor:      true,
		Vars: map[string]interface{}{
			"application_image_repository": applicationImageRepository,
			"application_image_tag":        applicationImageTag,
			"application_name":             applicationName,
			"namespace":                    applicationNamespace,
			"use_local_volume":             false,
		},
	})

	defer terraform.Destroy(t, terraformOptions)

	terraform.InitAndApplyAndIdempotent(t, terraformOptions)

	actualNamepaceName := terraform.Output(t, terraformOptions, "namespace_name")
	assert.Equal(t, applicationNamespace, actualNamepaceName)

	actualDeploymentName := terraform.Output(t, terraformOptions, "deployment_name")
	assert.Equal(t, applicationName, actualDeploymentName)

	actualServiceName := terraform.Output(t, terraformOptions, "service_name")
	assert.Equal(t, applicationName, actualServiceName)
}
