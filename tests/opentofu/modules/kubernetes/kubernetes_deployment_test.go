package test

import (
	"fmt"
	"os/exec"
	"path/filepath"
	"testing"
	"text/template"

	"os"

	"sigs.k8s.io/kind/pkg/cluster"

	"github.com/gruntwork-io/terratest/modules/docker"
	"github.com/gruntwork-io/terratest/modules/terraform"
	test_structure "github.com/gruntwork-io/terratest/modules/test-structure"
	"github.com/stretchr/testify/assert"
)

type ProviderConfig struct {
	ConfigPath string
	Context    string
}

const kindClusterName string = "kubernetes-deployment-test"
const kindConfigPath string = "../../resources/kube-config.yaml"
const kindContext string = "kind-" + kindClusterName
const providerTemplate = `
provider "kubernetes" {
	config_path = "{{.ConfigPath}}"
	config_context = "{{.Context}}"
}
`
const rootDirectory string = "../../../../"
const rootOpenTofuDirectory string = "../../../../deployments/opentofu/modules"

func TestMain(m *testing.M) {
	err := createKindCluster()
	if err != nil {
		println("Failed to create kind cluster")
		fmt.Printf("Error: %v", err)
		os.Exit(2)
	}

	exitVal := m.Run()

	err = deleteKindCluster()
	if err != nil {
		println("Failed to delete kind cluster")
		fmt.Printf("Error: %v", err)
		os.Exit(3)
	}

	os.Remove(kindConfigPath)

	os.Exit(exitVal)
}

func buildAndLoadDockerImage(t *testing.T, contextPath string, dockerfilePath string, tag string) {
	buildOptions := &docker.BuildOptions{
		Tags:         []string{tag, fmt.Sprintf("docker.io/library/%s", tag), fmt.Sprintf("localhost/%s", tag)},
		OtherOptions: []string{"-f", rootDirectory + dockerfilePath},
	}
	docker.Build(t, contextPath, buildOptions)
}

func createKindCluster() error {
	provider := cluster.NewProvider()
	err := provider.Create(
		kindClusterName,
		cluster.CreateWithNodeImage("kindest/node:v1.21.1"),
		cluster.CreateWithKubeconfigPath(kindConfigPath),
	)
	if err != nil {
		return err
	}
	return nil
}

func deleteKindCluster() error {
	provider := cluster.NewProvider()
	err := provider.Delete(kindClusterName, kindConfigPath)
	if err != nil {
		return err
	}
	return nil
}

func loadPodmanImageToKindCluster(image string) error {
	command := exec.Command("kind", "load", "docker-image", "-n", kindClusterName, image)
	err := command.Run()
	if err != nil {
		fmt.Printf("Error: %v", err)
		return err
	}

	return nil
}

func createKubernetesProviderFile(t *testing.T, config ProviderConfig, tempDirectory string) {
	// Validate template
	template, err := template.New("provider").Parse(providerTemplate)
	if err != nil {
		t.Fatalf("Failed to create template: %v", err)
	}

	// Create the destination file
	destFile, err := os.Create(tempDirectory + "/__testing_provider.tf")
	if err != nil {
		t.Fatalf("Failed to create destination file: %v", err)
	}
	defer destFile.Close()

	// Write the template to the destination file
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
	applicationName := "hello-world"
	applicationImageRepository := fmt.Sprintf("localhost/%s", applicationName)
	applicationImageTag := "local-test"
	applicationFullImageName := fmt.Sprintf("%s:%s", applicationImageRepository, applicationImageTag)
	// Build and load the docker image
	buildAndLoadDockerImage(t, rootDirectory, "containers/python/Dockerfile", applicationFullImageName)

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

	// retryable errors in terraform testing.
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: tempDirectory,
		NoColor:      true,
		Vars: map[string]interface{}{
			"use_local_volume":             false,
			"application_image_repository": applicationImageRepository,
			"application_image_tag":        applicationImageTag,
		},
	})

	defer terraform.Destroy(t, terraformOptions)

	terraform.InitAndApply(t, terraformOptions)

	output := terraform.Output(t, terraformOptions, "hello_world")
	assert.Equal(t, "Hello, World!", output)
}
