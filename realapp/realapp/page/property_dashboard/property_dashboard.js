frappe.pages['property-dashboard'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Real Estate Inventory',
		single_column: true
	});

	/* ---------------- CSS ---------------- */
	$(`<style>
        .dashboard-canvas { padding: 10px; background: #f4f7fb; min-height: 80vh; font-family: system-ui; }
        .tower-card { background:#fff; border-radius:8px; box-shadow:0 4px 6px rgba(0,0,0,.05); margin-bottom:30px; border:1px solid #e1e4e8; }
        .tower-header { background:linear-gradient(to right,#274162,#e14d49); color:#fff; padding:12px 20px; font-weight:600; display:flex; justify-content:space-between; align-items:center; }
        .floor-row { display:flex; padding:10px; border-bottom:1px solid #f0f0f0; }
        .floor-label { min-width:80px; text-align:center; font-weight:700; background:#e9ecef; border-radius:6px; padding:8px 0; margin-right:15px; }
        .units-grid { display:flex; flex-wrap:wrap; gap:10px; }

        .unit-card { width:115px; padding:10px; border-radius:6px; color:#fff; cursor:pointer; transition:.2s; box-shadow:0 2px 4px rgba(0,0,0,.1); }
        .unit-card:hover { transform:translateY(-3px); }

        .unit-name { font-weight:700; font-size:14px; }
        .unit-detail { font-size:10px; opacity:.9; line-height:1.3; }

        .status-Available { background:#28a745; }
        .status-Booked { background:#ffc107; color:#333; }
        .status-Sold { background:#dc3545; }
        .status-Blocked { background:#6c757d; }
        .status-Default { background:#17a2b8; }

        .badge { margin-left:6px; font-size:11px; }
        .default-filters { padding:10px 0; }
        .default-filters label { margin-right:20px; font-weight:500; }
    </style>`).appendTo(wrapper);

	/* ---------------- Filters ---------------- */
	page.project_filter = page.add_field({
		fieldname: 'project',
		label: 'Project',
		fieldtype: 'Link',
		options: 'Project',
		change: () => render_dashboard()
	});

	page.block_filter = page.add_field({
		fieldname: 'block',
		label: 'Block',
		fieldtype: 'MultiSelectList',
		get_data: function (txt) {
			return frappe.db.get_link_options('Block', txt);
		}
	});

	page.floor_filter = page.add_field({
		fieldname: 'floor_number',
		label: 'Floor',
		fieldtype: 'Int',
		change: () => render_dashboard()
	});

	page.unit_filter = page.add_field({
		fieldname: 'unit_name',
		label: 'Unit',
		fieldtype: 'Data',
		change: () => render_dashboard()
	});

	/* ✅ RESTORED: Status Filter */
	page.status_filter = page.add_field({
		fieldname: 'status',
		label: 'Status',
		fieldtype: 'Select',
		options: "\nAvailable\nBooked\nBlocked\nSold",
		change: () => render_dashboard()
	});

	// Immediate/live update listeners via event delegation on wrapper
	$(wrapper).on('input change', '[data-fieldname="floor_number"] input', () => {
		clearTimeout(page.floor_filter_timeout);
		page.floor_filter_timeout = setTimeout(() => render_dashboard(), 300);
	});
	$(wrapper).on('input change', '[data-fieldname="unit_name"] input', () => {
		clearTimeout(page.unit_filter_timeout);
		page.unit_filter_timeout = setTimeout(() => render_dashboard(), 300);
	});
	$(wrapper).on('click', '[data-fieldname="block"] .selectable-item, [data-fieldname="block"] .clear-selections, [data-fieldname="block"] .select-all-options', () => {
		setTimeout(() => render_dashboard(), 50);
	});

	/* ✅ RESTORED: Refresh Button */
	page.add_inner_button('Refresh', () => render_dashboard());

	/* ---------------- Default Checkbox Filters ---------------- */
	let inventory_filters = {
		share: "Tridasa Realty Ventures Pvt Ltd",
		mortgage: ["is", "not set"]
	};

	const checkbox_html = `
        <div class="default-filters">
            <label>
                <input type="checkbox" id="filter_share" checked>
                Share: Tridasa Realty Ventures Pvt Ltd
            </label>
            <label>
                <input type="checkbox" id="filter_mortgage" checked>
                Exclude Mortgaged Units
            </label>
        </div>
    `;
	$(wrapper).find('.layout-main-section').prepend(checkbox_html);

	$("#filter_share").on("change", function () {
		this.checked
			? inventory_filters.share = "Tridasa Realty Ventures Pvt Ltd"
			: delete inventory_filters.share;
		render_dashboard();
	});

	$("#filter_mortgage").on("change", function () {
		this.checked
			? inventory_filters.mortgage = ["is", "not set"]
			: delete inventory_filters.mortgage;
		render_dashboard();
	});

	$(wrapper).find('.layout-main-section')
		.append('<div id="inventory-board" class="dashboard-canvas">Loading...</div>');

	/* ---------------- Data Fetch ---------------- */
	function render_dashboard() {
		let filters = {};

		let project_val = page.project_filter.get_value();
		if (project_val) {
			filters.project = project_val;
		}

		let blocks = page.block_filter.get_value();
		if (blocks && blocks.length > 0) {
			filters.block = ['in', blocks];
		}

		let floor_val = $(wrapper).find('[data-fieldname="floor_number"] input').val();
		if (floor_val !== "" && floor_val !== null && floor_val !== undefined) {
			let parsed_floor = parseInt(floor_val);
			if (!isNaN(parsed_floor)) {
				filters.floor_number = parsed_floor;
			}
		}

		let unit_val = $(wrapper).find('[data-fieldname="unit_name"] input').val();
		if (unit_val) {
			filters.unit_name = ['like', `%${unit_val}%`];
		}

		if (page.status_filter.get_value())
			filters.status = page.status_filter.get_value();

		Object.assign(filters, inventory_filters);

		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Unit',
				fields: [
					'name', 'unit_name', 'status',
					'project', 'block', 'floor_number',
					'flat_type', 'salable_area', 'facing'
				],
				filters: filters,
				limit_page_length: 5000,
				order_by: 'floor_number desc'
			},
			callback: r => r.message
				? generate_html(r.message)
				: $('#inventory-board').html('<div class="text-center">No Units Found</div>')
		});
	}

	/* ---------------- HTML Builder ---------------- */
	function generate_html(data) {
		let tree = {};

		data.forEach(u => {
			let p = u.project || 'Project';
			let b = u.block || '-';
			let f = u.floor_number || 0;

			tree[p] ??= {};
			tree[p][b] ??= { floors: {}, counts: { Available: 0, Booked: 0, Sold: 0, Blocked: 0 } };
			tree[p][b].floors[f] ??= [];

			let status = u.status || 'Available';
			if (tree[p][b].counts[status] !== undefined)
				tree[p][b].counts[status]++;

			tree[p][b].floors[f].push(u);
		});

		let html = '';

		Object.keys(tree).forEach(p => {
			Object.keys(tree[p]).forEach(b => {
				const c = tree[p][b].counts;

				html += `
                <div class="tower-card">
                    <div class="tower-header">
                        <span>${p} - Block ${b}</span>
                        <span>
                            <span class="badge badge-success">Avail: ${c.Available}</span>
                            <span class="badge badge-warning">Booked: ${c.Booked}</span>
                            <span class="badge badge-danger">Sold: ${c.Sold}</span>
                            <span class="badge badge-secondary">Blocked: ${c.Blocked}</span>
                            <span class="badge badge-light">Total: ${c.Available + c.Booked + c.Sold + c.Blocked}</span>
                        </span>
                    </div>
                `;

				Object.keys(tree[p][b].floors)
					.map(Number).sort((a, b) => b - a)
					.forEach(f => {
						html += `
                        <div class="floor-row">
                            <div class="floor-label">Floor ${f}</div>
                            <div class="units-grid">
                        `;

						tree[p][b].floors[f].forEach(u => {
							let tooltip =
								`Area: ${u.salable_area} sft\nFacing: ${u.facing}\nType: ${u.flat_type}`;

							html += `
                            <div class="unit-card status-${u.status || 'Default'}"
                                 title="${tooltip}"
                                 onclick="frappe.set_route('Form','Unit','${u.name}')">
                                <div class="unit-name">${u.unit_name}</div>
                                <div class="unit-detail">${u.flat_type}</div>
                                <div class="unit-detail">${u.salable_area} sft | ${u.facing}</div>
                            </div>`;
						});

						html += `</div></div>`;
					});

				html += `</div>`;
			});
		});

		$('#inventory-board').html(html);
	}

	render_dashboard();
};
