report_dir = .
report_name = main

clean:
	# clean LaTeX artifacts
	@for file_ext in "*.pdf" "*.aux" "*.log" "*.toc" "*.out" "*.run.xml"; do \
		find $(report_dir) -name "$${file_ext}" -delete; \
	done
pdf: clean
	cd "${report_dir}"; \
	xelatex --shell-escape -interaction=nonstopmode "${report_name}"; \
	xelatex --shell-escape -interaction=nonstopmode "${report_name}"