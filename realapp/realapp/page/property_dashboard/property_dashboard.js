frappe.pages['property-dashboard'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Real Estate Inventory',
		single_column: true
	});

	// 1. Add Custom CSS for the "Beautiful" Dashboard Look
	$(`<style>
        .dashboard-canvas { padding: 5px; background: #f4f7fbff; min-height: 80vh; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        
        /* Tower (Block) Card */
        .tower-card { 
            background: #ffffffff; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(16, 81, 173, 0.05); 
            margin-bottom: 30px; 
            overflow: hidden; 
            border: 1px solid #e1e4e8;
        }
        .tower-header { 
            background: linear-gradient(to right, #274162, #e14d49); 
            color: white; 
            padding: 12px 20px; 
            font-size: 16px; 
            font-weight: 600; 
            display: flex; 
            justify-content: space-between;
            align-items: center;
        }
        
        /* Floor Row */
        .floor-row { 
            display: flex; 
            border-bottom: 1px solid #f0f0f0; 
            padding: 10px; 
            align-items: center; 
            transition: background 0.2s;
        }
        .floor-row:hover { background: #fafbfc; }
        .floor-row:last-child { border-bottom: none; }
        
        .floor-label { 
            min-width: 80px; 
            font-weight: 700; 
            color: #555; 
            font-size: 13px; 
            text-align: center;
            background: #e9ecef;
            padding: 8px 0;
            border-radius: 6px;
            margin-right: 15px;
        }

        /* Unit Grid */
        .units-grid { display: flex; flex-wrap: wrap; gap: 10px; flex-grow: 1; }
        
        .unit-card { 
            width: 110px; 
            padding: 10px; 
            border-radius: 6px; 
            color: white; 
            cursor: pointer; 
            position: relative;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .unit-card:hover { transform: translateY(-3px); box-shadow: 0 5px 10px rgba(0,0,0,0.2); z-index: 10; }
        
        .unit-name { font-weight: bold; font-size: 14px; display: block; margin-bottom: 4px; }
        .unit-detail { font-size: 10px; opacity: 0.9; line-height: 1.2; }
        
        /* Status Colors - Add more as needed */
        .status-Available { background-color: #28a745; /* Green */ }
        .status-Booked { background-color: #ffc107; color: #333; /* Yellow */ }
        .status-Sold { background-color: #dc3545; /* Red */ }
        .status-Blocked { background-color: #6c757d; /* Grey */ }
        .status-Default { background-color: #17a2b8; /* Blue */ }

    </style>`).appendTo(wrapper);

	// 2. Add Filters
	page.project_filter = page.add_field({
		fieldname: 'project',
		label: 'Project',
		fieldtype: 'Data', // Change to 'Link' if you have a Project DocType
		change: () => render_dashboard()
	});

	page.block_filter = page.add_field({
		fieldname: 'block',
		label: 'Block',
		fieldtype: 'Data',
		change: () => render_dashboard()
	});

	page.floor_filter = page.add_field({
		fieldname: 'floor_number',
		label: 'Floor No',
		fieldtype: 'Int',
		change: () => render_dashboard()
	});

	page.unit_filter = page.add_field({
		fieldname: 'unit_name',
		label: 'Unit Name',
		fieldtype: 'Data',
		change: () => render_dashboard()
	});

	page.add_inner_button('Refresh', () => render_dashboard());

	// Main Content Wrapper
	$(wrapper).find('.layout-main-section').append('<div id="inventory-board" class="dashboard-canvas">Loading...</div>');

	// 3. Logic to Fetch and Render Data
	function render_dashboard() {
		let filters = {};

		// Apply filters if values exist
		let project_val = page.project_filter.get_value();
		if (project_val) filters.project = ['like', `%${project_val}%`];

		let block_val = page.block_filter.get_value();
		if (block_val) filters.block = block_val;

		let floor_val = page.floor_filter.get_value();
		if (floor_val) filters.floor_number = floor_val;

		let unit_val = page.unit_filter.get_value();
		if (unit_val) filters.unit_name = ['like', `%${unit_val}%`];

		// Fetch Data
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Unit', // !!! REPLACE with your actual DocType Name !!!
				fields: ['name', 'unit_name', 'status', 'block', 'floor_number', 'flat_type', 'facing', 'salable_area', 'project'],
				filters: filters,
				limit_page_length: 5000,
				order_by: 'floor_number desc' // Important: Top floors shown first
			},
			callback: function (r) {
				if (r.message) {
					generate_html(r.message);
				} else {
					$('#inventory-board').html('<div class="text-muted text-center">No Units Found</div>');
				}
			}
		});
	}

	// 4. HTML Generation Logic
	function generate_html(data) {
		if (data.length === 0) {
			$('#inventory-board').html('<div class="text-center p-5">No records found matching criteria.</div>');
			return;
		}

		// Group Data: Project -> Block -> Floor -> Units
		let tree = {};
		data.forEach(u => {
			let proj = u.project || 'Unknown Project';
			let blk = u.block || 'Other';
			let flr = u.floor_number || 0;

			if (!tree[proj]) tree[proj] = {};
			if (!tree[proj][blk]) tree[proj][blk] = {};
			if (!tree[proj][blk][flr]) tree[proj][blk][flr] = [];

			tree[proj][blk][flr].push(u);
		});

		let html = '';

		// Iterate Projects
		Object.keys(tree).sort().forEach(proj => {

			// Iterate Blocks (Towers)
			Object.keys(tree[proj]).sort().forEach(blk => {
				html += `<div class="tower-card">
                            <div class="tower-header">
                                <span><i class="fa fa-building"></i> ${proj} - Block ${blk}</span>
                                <span style="font-size:12px; opacity:0.8">Tower View</span>
                            </div>`;

				// Iterate Floors (Descending Order for visual stacking)
				let floors = tree[proj][blk];
				let floor_nums = Object.keys(floors).map(Number).sort((a, b) => b - a);

				floor_nums.forEach(f_num => {
					html += `<div class="floor-row">
                                <div class="floor-label">Floor ${f_num}</div>
                                <div class="units-grid">`;

					// Render Units
					// Sort units by name or number if needed
					floors[f_num].sort((a, b) => a.unit_name.localeCompare(b.unit_name)).forEach(unit => {
						let statusClass = 'status-' + (unit.status || 'Default');

						// Tooltip info
						let tooltip = `Area: ${unit.salable_area} sft\nFacing: ${unit.facing}\nType: ${unit.flat_type}`;

						html += `<div class="unit-card ${statusClass}" title="${tooltip}" onclick="frappe.set_route('Form', 'Unit', '${unit.name}')">
                                    <span class="unit-name">${unit.unit_name}</span>
                                    <div class="unit-detail">${unit.flat_type}</div>
                                    <div class="unit-detail">${unit.status}</div>
                                 </div>`;
					});

					html += `   </div>
                             </div>`;
				});

				html += `</div>`;
			});
		});

		$('#inventory-board').html(html);
	}

	// Initial Load
	render_dashboard();
};