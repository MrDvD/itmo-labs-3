module decoder_testbench;
	reg sel1, sel2;
	wire [1:0] d1, d2;
	parameter N = 8;
	reg [$clog2(N)-1:0] sel3;
	wire [N-1:0] d3;
	reg clk, rst;
	
	
	decoder_1_assign first_decoder(sel1, d1);
	decoder_1_always second_decoder(sel2, d2);
	decoder_2_parametric #(.N(N)) third_decoder(sel3, d3);
	result_keeper #(.N(N)) keeper_element(clk, rst, d3);
	
	initial begin
		// first decoder
		sel1 = 1'b0;
		#1;
		$display("first: expected 1 - found %0d", d1);
		sel1 = 1'b1;
		#1;
		$display("first: expected 2 - found %0d", d1);
	end
	
	initial begin
		// second decoder
		sel2 = 1'b0;
		#1;
		$display("second: expected 1 - found %0d", d2);
		sel2 = 1'b1;
		#1;
		$display("second: expected 2 - found %0d", d2);
	end
	
	initial begin
		// third decoder
		for (int i = 0; i < N; i++) begin
			sel3 = i;
			#1;
			$display("third: expected %0d - found %0d", 1 << i, d3);
		end
	end
	
	initial begin
		// init keeper element
		$display("keeper: initial value - %0d", keeper_element.result);
		clk = 0;
		rst = 1;
		forever #5 clk = ~clk;
	end
	
	initial begin
		// test keeper
		for (int i = 1; i <= 8; i++) begin
			if (i == 3) begin
				$display("setting rst");
				rst = 0;
			end
			if (i == 6) begin
				$display("unsetting rst");
				rst = 1;
			end
			#6;
			$display("keeper: saved value #%0d - %0d", i, keeper_element.result);
		end
	end
endmodule

module decoder_1_assign
(
	input wire q,
	output wire [1:0] d
);
	assign d = (q == 1'b0) ? 2'b01 : 2'b10;
endmodule

module decoder_1_always
(
	input wire q,
	output reg [1:0] d
);	
	always @(*) begin
		d = (q == 1'b0) ? 2'b01 : 2'b10;
	end
endmodule

module decoder_2_parametric
#(
	parameter int N = 2
)
(
	input wire [$clog2(N)-1:0] q,
	output reg [N-1:0] d
);
	wire [N-1:0] d_result;
	assign d_result = {{(N-1){1'b0}}, 1'b1} << q;
	always @(*) begin
		d = d_result;
	end
endmodule

module result_keeper
#(
	parameter int N = 2
)
(
	input wire clk, rst,
	input wire [N-1:0] q
);
	reg [N-1:0] result = 0;
	always @(posedge clk) begin
		if (~rst)
			result <= 0;
		else
			result <= q;
	end
endmodule