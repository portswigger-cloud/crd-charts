# crd-charts

> [!WARNING]
> **Retired (October 2026). Nothing consumes these charts any more, and no new versions are built.**
>
> The CRDs these charts carried are now owned by Argo CD through
> [portswigger-cloud/system](https://github.com/portswigger-cloud/system):
>
> | CRDs | Now |
> |---|---|
> | Traefik | `system/base/traefik-crds` (copied into each section running Traefik) |
> | AWS Load Balancer Controller | `system/base/aws-load-balancer-controller-crds`; observability's controller renders its own |
> | SealedSecret | `system/base/sealed-secrets-crds` |
> | NACK (jetstream.nats.io) | `system/platform/nack-crds` |
> | ARC (actions.github.com) | rendered by the `arc` release itself (`crd-sync-options`) |
> | grafana-alloy PodLogs | rendered by system's grafana-alloy (`crds.create: true`) |
>
> bsee's `prod-apse2` is not on Argo yet (PLAT-940); there the bsee helmfile
> applies the Traefik and ALB controller CRDs through presync hooks, pinned to the
> versions vendored in system.
>
> Every version ever published stays available on GitHub Pages and on GHCR
> (`oci://ghcr.io/portswigger-cloud/crd-charts/<chart>`), so old pins still resolve.

Helm charts for containing the CRDs for common helm applications.

This is an attempt to ease the Helm / CRD management issue by creating charts that contain the CRDs
for various Helm charts 

You can read more about the problem here: https://helm.sh/docs/chart_best_practices/custom_resource_definitions/

We have opted for [Method 2: Separate Charts](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/#method-2-separate-charts).

## How does it work?

Charts are added to `helmfile.yaml` as releases (we're mis-using `helmfile` to make updates easy and visible), `helmfile` is used to fetch
the charts and run some hooks to create the crd charts and the charts are deployed to GitHub Pages.

### Chart Names
The name of the CRDs chart for a Helm chart is:
```
$repo-$chartName-crds
```

For example, for the `cert-manager` chart in the `jetstack` Helm repository the name of the CRDs chart is:
```
jetstack-cert-manager-crds
```

and can be installed by running:
```
helm repo add crd-charts https://portswigger-cloud.github.io/crd-charts/
helm install cert-manager-crds crd-charts/jetstack-cert-manager-crds
```

### Installing from GHCR (OCI)
Charts are also published as OCI artifacts to GHCR, at `oci://ghcr.io/portswigger-cloud/crd-charts/$repo-$chartName-crds`.
They are private to the organisation, so a `helm registry login ghcr.io` is needed first. In a `helmfile.yaml`:
```yaml
releases:
  - name: cert-manager-crds
    chart: oci://ghcr.io/portswigger-cloud/crd-charts/jetstack-cert-manager-crds
    version: v1.2.3
```

GitHub Pages publishing continues during the migration and will be removed once nothing references it.

### Versions
The CRDs charts _should_ be versioned matching the Helm chart. Often, there will be no changes between versions.

There is the chance that a version may not be available
(**There's no guarantee that a chart version will have been generated. Check the releases on this repository or https://portswigger-cloud.github.io/crd-charts/index.yaml**).

## Known Issues
### Duplicate CRDs in different charts
There are charts which contain CRDs that other charts also contain. For example, `tempo-distributed` and `mimir-distributed`
both contain the same CRDs. Some of the CRDs in those charts exist in the `kube-prometheus` (prometheus-operator) chart.
Currently, I'm trying to think of a fix for this :-/

