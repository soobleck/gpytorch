import torch
import gpytorch
from torch.autograd import Variable
from gpytorch.lazy import DiagLazyVariable


diag = torch.Tensor([1, 2, 3])


def test_evaluate():
    diag_lv = DiagLazyVariable(Variable(diag))
    assert torch.equal(diag_lv.evaluate().data, diag.diag())


def test_function_factory():
    # 1d
    diag_var1 = Variable(diag, requires_grad=True)
    diag_var2 = Variable(diag, requires_grad=True)
    test_mat = torch.Tensor([3, 4, 5])

    diag_lv = DiagLazyVariable(diag_var1)
    diag_ev = DiagLazyVariable(diag_var2).evaluate()

    # Forward
    res = diag_lv.inv_matmul(Variable(test_mat))
    actual = gpytorch.inv_matmul(diag_ev, Variable(test_mat))
    # assert torch.norm(res.data - actual.data) < 1e-4

    # Backward
    res.sum().backward()
    actual.sum().backward()
    # assert torch.norm(diag_var1.grad.data - diag_var2.grad.data) < 1e-3

    # 2d
    diag_var1 = Variable(diag, requires_grad=True)
    diag_var2 = Variable(diag, requires_grad=True)
    test_mat = torch.eye(3)

    diag_lv = DiagLazyVariable(diag_var1)
    diag_ev = DiagLazyVariable(diag_var2).evaluate()

    # Forward
    res = diag_lv.inv_matmul(Variable(test_mat))
    actual = gpytorch.inv_matmul(diag_ev, Variable(test_mat))
    assert torch.norm(res.data - actual.data) < 1e-4

    # Backward
    res.sum().backward()
    actual.sum().backward()
    assert torch.norm(diag_var1.grad.data - diag_var2.grad.data) < 1e-3


def test_batch_function_factory():
    # 2d
    diag_var1 = Variable(diag.repeat(5, 1), requires_grad=True)
    diag_var2 = Variable(diag.repeat(5, 1), requires_grad=True)
    test_mat = torch.eye(3).repeat(5, 1, 1)

    diag_lv = DiagLazyVariable(diag_var1)
    diag_ev = DiagLazyVariable(diag_var2).evaluate()

    # Forward
    res = diag_lv.matmul(Variable(test_mat))
    actual = torch.matmul(diag_ev, Variable(test_mat))
    assert torch.norm(res.data - actual.data) < 1e-4

    # Backward
    res.sum().backward()
    actual.sum().backward()
    assert torch.norm(diag_var1.grad.data - diag_var2.grad.data) < 1e-3


def test_get_item():
    diag_lv = DiagLazyVariable(Variable(diag))
    diag_ev = diag_lv.evaluate()
    assert torch.equal(diag_lv[0:2].evaluate().data, diag_ev[0:2].data)


def test_get_indices():
    diag_lv = DiagLazyVariable(Variable(diag))
    res = diag_lv._get_indices(Variable(torch.LongTensor([1, 2, 0])),
                               Variable(torch.LongTensor([0, 2, 0])))
    assert torch.equal(res.data, torch.Tensor([0, 3, 1]))
