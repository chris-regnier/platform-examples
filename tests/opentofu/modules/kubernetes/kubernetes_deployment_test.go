package test

import (
	"fmt"
	"os/exec"
	"path/filepath"
	"testing"
	"text/template"

	"os"

	"sigs.k8s.io/kind/pkg/cluster"

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
const rootDirectory string = "../../../../deployments/opentofu/modules"

func TestMain(m *testing.M) {
	err := createKindCluster()
	if err != nil {
		println("Failed to create kind cluster")
		fmt.Printf("Error: %v", err)
		os.Exit(2)
	}

	loadPodmanImageToKindCluster("localhost/platform-examples-python:local")

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
	command := exec.Command("kind", "load", image)
	err := command.Run()
	if err != nil {
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
	tempDirectory := test_structure.CopyTerraformFolderToTemp(t, rootDirectory, "kubernetes-deployment")
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
			"use_local_volume": false,
		},
	})

	defer terraform.Destroy(t, terraformOptions)

	terraform.InitAndApply(t, terraformOptions)

	output := terraform.Output(t, terraformOptions, "hello_world")
	assert.Equal(t, "Hello, World!", output)
}
