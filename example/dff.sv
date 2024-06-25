// dff.sv

`timescale 1ns/1ns

module dff (
    output logic q,
    input logic clk, d
);

always @(posedge clk) begin
    q <= d;
end

endmodule
