report_dir := $(shell yq eval '.report.dir' config.yml)
report_name := $(shell yq eval '.report.name' config.yml)

clean:
	# clean LaTeX artifacts
	@for file_ext in "*.pdf" "*.aux" "*.log" "*.toc" "*.out"; do \
		find $(report_dir) -name "$${file_ext}" -delete; \
	done
	# clean project compiled files
	find . -name "*.compiled.*" -delete
pdf:
# 	python3 src/main.py
	cd "${report_dir}"; \
	xelatex --shell-escape -interaction=nonstopmode "${report_name}"; \
	xelatex --shell-escape -interaction=nonstopmode "${report_name}"