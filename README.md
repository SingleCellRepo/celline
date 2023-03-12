<br/><br/>

<div align="center">
  <img src="https://user-images.githubusercontent.com/104006202/219851803-967b3ef8-c6f9-447b-8ba4-4771e1989513.jpg" width="250px" >

<br/>

<span> <font size=3em>celline - Single-<strong>Cell</strong> RNA analysis pipe<strong>Line</strong> with Public DB </font></span>

<br/>

![Activity](https://img.shields.io/badge/dynamic/json?label=Latest%20event&query=%24%5B0%5D.created_at&url=https%3A%2F%2Fapi.github.com%2Fusers%2Fkcabo%2Fevents)

[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/c/celline)
![workflow](https://img.shields.io/github/actions/workflow/status/SingleCellRepo/celline/unit-tests.yml)
![license](https://img.shields.io/github/license/SingleCellRepo/celline)

<br/>

<span><font size=5px>Contributors</font></span>

<a href="https://github.com/SingleCellRepo/celline/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=SingleCellRepo/celline" />
</a>
<br/>Yuya Sato

</div>
<br/><br/>

## 🧑‍💻 About This Project

Single-cell RNA-seq records RNA expression per single cell, which has been the focus of much attention in recent years, and allows analysis of samples consisting of multicellular systems compared to Bulk RNA-seq. However, data acquisition is very costly and not suitable for simple validation.

Public resources such as SRA and GEO are comprehensive databases of genetic data that have been submitted so far. However, it is difficult to collect and reanalyze single-cell RNA-seq data from these data due to the complexity of collection and data structure.

In this study, we constructed a system that enables users to easily obtain Single-cell RNA-seq data in large quantities.

Users can prepare the necessary environment for analysis, download data, and find biological events in one step.

## 💻 Installation

### 1. Clone this repository.

```bash
git clone https://github.com/SingleCellRepo/celline.git
```

### 2. Install.

```bash
make install
```

### 3. Frontend installation.

1. Install npm
   see https://nodejs.org/ja/download/
2. Install yarn
   see https://classic.yarnpkg.com/lang/en/docs/install
3. Install requrement

```bash
cd frontend && yarn install
```

Please install all requrements following CUI instruction.

## 👟 How to Use

### Create New Project

```bash
cd <project_directory>
celline init <project_name>
```

### Add SRA, GEO Dataset References into Your Project.

```bash
celline add <SRA, GSE, GSM ID>
```

### Download scRNA-seq Raw Data

```bash
celline dump
```

### Count Downloaded Data

```bash
celline count
```

### Make Analyzable Seurat Object

```bash
celline mkseurat
```

### Integrate scRNA-seq Data with Seurat

```bash
celline integrate <target_GSM_ID>
```

## License

This project is available under the MIT License. See the LICENSE file for more information.

## Contact

If you have any questions or suggestions regarding this project, contact [Yuya Sato](yu.pisces.556223@akane.waseda.jp).

## Acknowledgement

This project was supported by Toru Asahi, Kosuke Kataoka. We would like to take this opportunity to express our gratitude.
